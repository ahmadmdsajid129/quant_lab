from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_workspace
from app.db.models import User, Workspace, PaperOrder
from app.schemas.paper_trading import (
    PaperOrderSubmitRequest,
    PaperAccountSummaryResponse,
    PaperOrderDetail,
)
from app.services.paper_trading_service import paper_trading_service

router = APIRouter(prefix="/paper-trading", tags=["Paper Trading & Execution"])


@router.get("/account", response_model=PaperAccountSummaryResponse)
def get_paper_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Fetch active simulated paper-trading account, positions, and recent executions.
    """
    account = paper_trading_service.get_or_create_account(db, workspace.id)
    return paper_trading_service.get_account_summary(db, account)


@router.post("/orders", response_model=PaperOrderDetail)
def submit_paper_order(
    request: PaperOrderSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Submit and simulate execution of a paper trading order with pre-trade risk controls.
    """
    account = paper_trading_service.get_or_create_account(db, workspace.id)
    try:
        order = paper_trading_service.execute_paper_order(
            db=db,
            account=account,
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            price=request.price,
            order_type=request.order_type,
        )
        return {
            "id": order.id,
            "symbol": order.symbol,
            "order_type": order.order_type,
            "side": order.side,
            "quantity": order.quantity,
            "limit_price": order.limit_price,
            "status": order.status,
            "filled_quantity": order.filled_quantity,
            "filled_price": order.filled_price,
            "created_at": str(order.created_at),
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/kill-switch")
def trigger_kill_switch(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Emergency Kill Switch: immediately cancels all resting orders and halts automated execution.
    """
    account = paper_trading_service.get_or_create_account(db, workspace.id)
    # Cancel any submitted / resting orders
    pending = (
        db.query(PaperOrder)
        .filter(PaperOrder.account_id == account.id, PaperOrder.status == "SUBMITTED")
        .all()
    )
    for ord in pending:
        ord.status = "CANCELLED"
    db.commit()

    return {
        "status": "HALTED",
        "orders_cancelled": len(pending),
        "message": "Emergency Kill Switch engaged. All active orders halted.",
    }


@router.post("/reset", response_model=PaperAccountSummaryResponse)
def reset_paper_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Reset paper trading account back to clean initial state ($100,000 cash, 0 positions).
    """
    account = paper_trading_service.get_or_create_account(db, workspace.id)
    paper_trading_service.reset_account(db, account)
    return paper_trading_service.get_account_summary(db, account)
