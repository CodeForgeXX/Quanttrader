from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Position:
    symbol: str
    side: str          # LONG / SHORT
    entry_price: float
    quantity: float

    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    opened_at: datetime = datetime.now()

    status: str = "OPEN"


@dataclass
class TradeResult:
    symbol: str

    pnl: float

    pnl_percent: float

    closed_at: datetime

    reason: str