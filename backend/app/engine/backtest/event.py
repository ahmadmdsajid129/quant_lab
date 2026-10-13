from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from app.engine.strategy.base import BaseStrategy
from app.engine.backtest.metrics import compute_performance_metrics


class EventBacktestEngine:
    """
    Event-driven simulation engine with strict non-negotiable time semantics:
    - Bar t signal executes at bar t+1 Open.
    - Transaction cost attribution: Commission (bps) + Slippage (%) + Short Borrow Financing.
    - Strict Cash, Position, and Trade-log accounting.
    """
    def __init__(
        self,
        initial_capital: float = 100_000.0,
        commission_bps: float = 5.0,        # 5 bps (0.05%)
        slippage_pct: float = 0.05,         # 0.05% slippage on fill price
        borrow_rate_annual: float = 0.02,   # 2% annual borrow rate for shorts
    ):
        self.initial_capital = initial_capital
        self.commission_rate = commission_bps / 10_000.0
        self.slippage_pct = slippage_pct / 100.0
        self.borrow_rate_daily = borrow_rate_annual / 252.0

    def run(self, df: pd.DataFrame, strategy: BaseStrategy) -> Dict[str, Any]:
        """
        Execute event simulation.
        df must contain ['timestamp', 'open', 'high', 'low', 'close', 'volume'].
        """
        n_bars = len(df)
        if n_bars < 2:
            raise ValueError("Backtest requires at least 2 bars")

        # 1. Generate target signals from strategy (MUST ONLY USE INFORMATION <= t)
        signals = strategy.generate_signals(df).fillna(0.0).values

        # State tracking arrays
        cash = float(self.initial_capital)
        shares = 0.0
        total_fees = 0.0

        equity_curve = np.zeros(n_bars)
        equity_curve[0] = cash

        trade_logs: List[Dict[str, Any]] = []
        open_trade: Optional[Dict[str, Any]] = None

        # 2. Sequential bar-by-bar simulation
        for t in range(n_bars - 1):
            target_signal = signals[t]  # Target position weight at close of bar t
            
            # Next bar prices (execution occurs at t+1 Open)
            next_timestamp = df["timestamp"].iloc[t + 1]
            next_open = float(df["open"].iloc[t + 1])
            next_close = float(df["close"].iloc[t + 1])

            # Valuation before trading at t+1 Open
            current_portfolio_value = cash + (shares * next_open)
            target_notional = current_portfolio_value * target_signal
            target_shares = target_notional / next_open if next_open > 0 else 0.0

            # Required order
            delta_shares = target_shares - shares

            if abs(delta_shares) > 1e-4:
                # Trade execution with slippage
                if delta_shares > 0:  # Buy
                    exec_price = next_open * (1.0 + self.slippage_pct)
                    trade_side = "LONG"
                else:  # Sell
                    exec_price = next_open * (1.0 - self.slippage_pct)
                    trade_side = "SHORT"

                trade_notional = abs(delta_shares) * exec_price
                commission = trade_notional * self.commission_rate
                trade_fees = commission

                # Deduct cash
                cash -= (delta_shares * exec_price) + trade_fees
                total_fees += trade_fees

                # Track completed trade if closing or reversing position
                if shares != 0.0 and np.sign(target_shares) != np.sign(shares) and open_trade:
                    # Closing trade
                    exit_price = exec_price
                    entry_price = open_trade["entry_price"]
                    closed_qty = abs(open_trade["quantity"])
                    
                    if open_trade["side"] == "LONG":
                        gross_pnl = (exit_price - entry_price) * closed_qty
                    else:
                        gross_pnl = (entry_price - exit_price) * closed_qty

                    net_pnl = gross_pnl - open_trade["fees"] - trade_fees
                    return_pct = gross_pnl / (entry_price * closed_qty) if entry_price > 0 else 0.0

                    trade_logs.append({
                        "symbol": str(df.get("symbol", pd.Series(["ASSET"])).iloc[0]),
                        "entry_time": str(open_trade["entry_time"]),
                        "exit_time": str(next_timestamp),
                        "side": open_trade["side"],
                        "quantity": round(closed_qty, 4),
                        "entry_price": round(entry_price, 4),
                        "exit_price": round(exit_price, 4),
                        "gross_pnl": round(gross_pnl, 2),
                        "fees": round(open_trade["fees"] + trade_fees, 2),
                        "net_pnl": round(net_pnl, 2),
                        "return_pct": round(return_pct * 100.0, 2),
                    })
                    open_trade = None

                # Open new trade record if establishing new position
                if target_shares != 0.0 and open_trade is None:
                    open_trade = {
                        "entry_time": next_timestamp,
                        "entry_price": exec_price,
                        "side": "LONG" if target_shares > 0 else "SHORT",
                        "quantity": target_shares,
                        "fees": trade_fees,
                    }

                shares = target_shares

            # Deduct short borrow fee if holding short position
            if shares < 0:
                short_val = abs(shares * next_close)
                borrow_fee = short_val * self.borrow_rate_daily
                cash -= borrow_fee
                total_fees += borrow_fee

            # End of bar t+1 valuation at Close
            equity_curve[t + 1] = cash + (shares * next_close)

        # Performance metrics
        trade_net_pnls = [t["net_pnl"] for t in trade_logs]
        equity_series = pd.Series(equity_curve, index=df["timestamp"])
        metrics = compute_performance_metrics(equity_series, trade_pnls=trade_net_pnls)

        # Drawdown array
        cum_max = np.maximum.accumulate(equity_curve)
        drawdown_curve = (equity_curve - cum_max) / cum_max

        # Output payload
        results = {
            "initial_capital": self.initial_capital,
            "final_capital": round(float(equity_curve[-1]), 2),
            "total_fees_paid": round(float(total_fees), 2),
            "metrics": metrics,
            "equity_curve": [
                {"timestamp": str(ts), "equity": round(float(eq), 2), "drawdown": round(float(dd), 4)}
                for ts, eq, dd in zip(df["timestamp"], equity_curve, drawdown_curve)
            ],
            "trade_logs": trade_logs,
        }
        return results
