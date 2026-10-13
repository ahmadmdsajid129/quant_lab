from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PaperOrderSubmitRequest(BaseModel):
    symbol: str = Field(..., description="Instrument symbol (e.g. BTC/USD, AAPL)")
    side: str = Field(..., description="BUY or SELL")
    quantity: float = Field(..., gt=0.0)
    price: float = Field(..., gt=0.0)
    order_type: str = Field(default="MARKET", description="MARKET or LIMIT")


class PositionDetail(BaseModel):
    id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    pnl_pct: float


class PaperOrderDetail(BaseModel):
    id: str
    symbol: str
    order_type: str
    side: str
    quantity: float
    limit_price: Optional[float]
    status: str
    filled_quantity: float
    filled_price: Optional[float]
    created_at: str


class PaperAccountSummaryResponse(BaseModel):
    account_id: str
    name: str
    currency: str
    initial_cash: float
    current_cash: float
    positions_market_value: float
    total_equity: float
    unrealized_pnl: float
    total_return_pct: float
    positions: List[PositionDetail]
    recent_orders: List[PaperOrderDetail]
