from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class LOBPriceLevel(BaseModel):
    price: float
    quantity: float
    order_count: int


class LOBTrade(BaseModel):
    trade_id: str
    price: float
    quantity: float
    taker_side: str
    timestamp: float


class LOBSnapshotResponse(BaseModel):
    symbol: str
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    mid_price: Optional[float]
    microprice: Optional[float]
    order_flow_imbalance: float
    total_open_orders: int
    bids: List[LOBPriceLevel]
    asks: List[LOBPriceLevel]
    recent_trades: List[LOBTrade]


class LOBSimulateRequest(BaseModel):
    symbol: str = Field(default="BTC/USD")
    initial_mid: float = Field(default=100.0, ge=1.0)
    tick_size: float = Field(default=0.05, ge=0.001)
    num_events: int = Field(default=150, ge=10, le=2000)
    seed: int = Field(default=42)


class LOBOrderRequest(BaseModel):
    symbol: str = Field(default="BTC/USD")
    side: str = Field(..., description="BID or ASK")
    price: float = Field(..., ge=0.01)
    quantity: float = Field(..., ge=0.001)
