from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models import PaperAccount, PaperPosition, PaperOrder


class PaperTradingService:
    @staticmethod
    def get_or_create_account(db: Session, workspace_id: str) -> PaperAccount:
        account = db.query(PaperAccount).filter(PaperAccount.workspace_id == workspace_id).first()
        if not account:
            account = PaperAccount(
                workspace_id=workspace_id,
                name="Primary Paper Trading Account",
                initial_cash=100_000.0,
                current_cash=100_000.0,
                currency="USD",
            )
            db.add(account)
            db.commit()
            db.refresh(account)
        return account

    @staticmethod
    def get_account_summary(db: Session, account: PaperAccount) -> Dict[str, Any]:
        positions = db.query(PaperPosition).filter(PaperPosition.account_id == account.id).all()
        orders = (
            db.query(PaperOrder)
            .filter(PaperOrder.account_id == account.id)
            .order_by(PaperOrder.created_at.desc())
            .limit(20)
            .all()
        )

        positions_market_value = sum(p.quantity * p.current_price for p in positions)
        unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        total_equity = account.current_cash + positions_market_value
        total_return_pct = ((total_equity - account.initial_cash) / account.initial_cash) * 100.0

        return {
            "account_id": account.id,
            "name": account.name,
            "currency": account.currency,
            "initial_cash": account.initial_cash,
            "current_cash": round(account.current_cash, 2),
            "positions_market_value": round(positions_market_value, 2),
            "total_equity": round(total_equity, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "total_return_pct": round(total_return_pct, 2),
            "positions": [
                {
                    "id": p.id,
                    "symbol": p.symbol,
                    "side": p.side,
                    "quantity": p.quantity,
                    "entry_price": round(p.entry_price, 2),
                    "current_price": round(p.current_price, 2),
                    "unrealized_pnl": round(p.unrealized_pnl, 2),
                    "pnl_pct": round(((p.current_price - p.entry_price) / p.entry_price) * 100.0, 2)
                    if p.entry_price > 0 else 0.0,
                }
                for p in positions
            ],
            "recent_orders": [
                {
                    "id": o.id,
                    "symbol": o.symbol,
                    "order_type": o.order_type,
                    "side": o.side,
                    "quantity": o.quantity,
                    "limit_price": o.limit_price,
                    "status": o.status,
                    "filled_quantity": o.filled_quantity,
                    "filled_price": o.filled_price,
                    "created_at": str(o.created_at),
                }
                for o in orders
            ],
        }

    @staticmethod
    def execute_paper_order(
        db: Session,
        account: PaperAccount,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        order_type: str = "MARKET",
        slippage_pct: float = 0.0005,
        commission_bps: float = 2.0,
    ) -> PaperOrder:
        """
        Validate pre-trade risk and simulate order fill with transaction friction.
        """
        side = side.upper()
        if side not in ["BUY", "SELL"]:
            raise ValueError("Side must be BUY or SELL.")

        if quantity <= 0 or price <= 0:
            raise ValueError("Quantity and price must be strictly positive.")

        gross_notional = quantity * price
        if gross_notional > 50_000.0:
            raise ValueError(f"Order notional (${gross_notional:,.2f}) exceeds risk limit of $50,000 per order.")

        # Slippage and commission
        if side == "BUY":
            fill_price = price * (1.0 + slippage_pct)
        else:
            fill_price = price * (1.0 - slippage_pct)

        fill_notional = quantity * fill_price
        commission = fill_notional * (commission_bps / 10000.0)
        total_cost = fill_notional + commission

        # Pre-trade cash check for BUY
        if side == "BUY" and total_cost > account.current_cash:
            raise ValueError(f"Insufficient buying power: required ${total_cost:,.2f}, available ${account.current_cash:,.2f}.")

        # Existing position lookup
        pos = (
            db.query(PaperPosition)
            .filter(PaperPosition.account_id == account.id, PaperPosition.symbol == symbol)
            .first()
        )

        # Pre-trade check for SELL
        if side == "SELL" and (not pos or pos.quantity < quantity):
            avail = pos.quantity if pos else 0.0
            raise ValueError(f"Insufficient position to sell {quantity} units of {symbol}. Available: {avail}.")

        # Record order
        order = PaperOrder(
            account_id=account.id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            limit_price=price if order_type == "LIMIT" else None,
            status="FILLED",
            filled_quantity=quantity,
            filled_price=round(fill_price, 4),
        )
        db.add(order)

        # Update cash and positions
        if side == "BUY":
            account.current_cash -= total_cost
            if not pos:
                pos = PaperPosition(
                    account_id=account.id,
                    symbol=symbol,
                    side="LONG",
                    quantity=quantity,
                    entry_price=fill_price,
                    current_price=fill_price,
                    unrealized_pnl=0.0,
                )
                db.add(pos)
            else:
                total_qty = pos.quantity + quantity
                blended_px = ((pos.quantity * pos.entry_price) + (quantity * fill_price)) / total_qty
                pos.quantity = total_qty
                pos.entry_price = blended_px
                pos.current_price = fill_price
                pos.unrealized_pnl = (pos.current_price - pos.entry_price) * pos.quantity
        else:  # SELL
            net_proceeds = fill_notional - commission
            account.current_cash += net_proceeds
            pos.quantity -= quantity
            if pos.quantity <= 1e-6:
                db.delete(pos)
            else:
                pos.current_price = fill_price
                pos.unrealized_pnl = (pos.current_price - pos.entry_price) * pos.quantity

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def reset_account(db: Session, account: PaperAccount) -> None:
        db.query(PaperPosition).filter(PaperPosition.account_id == account.id).delete()
        db.query(PaperOrder).filter(PaperOrder.account_id == account.id).delete()
        account.current_cash = account.initial_cash
        db.commit()


paper_trading_service = PaperTradingService()
