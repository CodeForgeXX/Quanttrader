from dataclasses import dataclass, field
from typing import Optional

from src.models import Position


@dataclass
class TradingContext:
    """
    Holds the current trading session state.
    """

    symbol: Optional[str] = None
    timeframe: Optional[str] = None

    account_balance: float = 0.0

    current_signal: Optional[str] = None

    active_position: Optional[Position] = None

    metadata: dict = field(default_factory=dict)