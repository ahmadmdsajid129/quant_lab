from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.db.models import User
from app.schemas.microstructure import (
    LOBSimulateRequest,
    LOBSnapshotResponse,
    LOBOrderRequest,
)
from app.engine.microstructure.lob import LimitOrderBook, OrderSide
from app.engine.microstructure.simulator import simulate_synthetic_order_book

router = APIRouter(prefix="/microstructure", tags=["Market Microstructure & LOB"])

# Active session book cache for live interactive order placement
_ACTIVE_BOOKS: Dict[str, LimitOrderBook] = {}


def get_or_create_book(symbol: str) -> LimitOrderBook:
    if symbol not in _ACTIVE_BOOKS:
        _ACTIVE_BOOKS[symbol] = simulate_synthetic_order_book(symbol=symbol, seed=42)
    return _ACTIVE_BOOKS[symbol]


@router.post("/simulate", response_model=LOBSnapshotResponse)
def simulate_order_book(
    request: LOBSimulateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Run stochastic Poisson order arrival simulation and return full L2 ladder depth & trade tape.
    """
    lob = simulate_synthetic_order_book(
        symbol=request.symbol,
        initial_mid=request.initial_mid,
        tick_size=request.tick_size,
        num_events=request.num_events,
        seed=request.seed,
    )
    _ACTIVE_BOOKS[request.symbol] = lob
    return lob.get_depth_snapshot(levels=10)


@router.get("/snapshot", response_model=LOBSnapshotResponse)
def get_order_book_snapshot(
    symbol: str = "BTC/USD",
    current_user: User = Depends(get_current_user),
):
    """
    Fetch current L2 depth ladder, microprice, and recent tape for symbol.
    """
    lob = get_or_create_book(symbol)
    return lob.get_depth_snapshot(levels=10)


@router.post("/order", response_model=LOBSnapshotResponse)
def submit_limit_order(
    request: LOBOrderRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Submit a limit order directly to the active matching engine.
    Crosses matching asks/bids if marketable, else rests in the price-time queue.
    """
    side = request.side.upper()
    if side not in ["BID", "ASK"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order side must be BID or ASK.",
        )

    lob = get_or_create_book(request.symbol)
    lob.add_limit_order(
        side=OrderSide.BID if side == "BID" else OrderSide.ASK,
        price=request.price,
        quantity=request.quantity,
    )
    return lob.get_depth_snapshot(levels=10)
