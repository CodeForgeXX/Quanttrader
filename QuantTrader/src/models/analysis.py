from dataclasses import dataclass, field


@dataclass
class MarketAnalysis:

    # =====================
    # Basic
    # =====================

    symbol: str
    price: float

    ema20: float
    ema50: float
    ema200: float

    volume: float
    avg_volume: float

    # =====================
    # Trend
    # =====================

    trend: str = ""
    trend_score: int = 0

    # =====================
    # Market Structure
    # =====================

    structure: str = ""

    bos: bool = False
    choch: bool = False

    bos_count: int = 0
    choch_count: int = 0

    # =====================
    # Swing
    # =====================

    swing_highs: list = field(default_factory=list)
    swing_lows: list = field(default_factory=list)

    # =====================
    # Liquidity
    # =====================

    liquidity: bool = False

    buy_side_liquidity: bool = False
    sell_side_liquidity: bool = False

    liquidity_grab: bool = False

    equal_highs: list = field(default_factory=list)
    equal_lows: list = field(default_factory=list)

    # =====================
    # Order Block
    # =====================

    bullish_ob: bool = False
    bearish_ob: bool = False

    bullish_ob_price: float = 0.0
    bearish_ob_price: float = 0.0

    ob_strength: int = 0

    mitigated: bool = False

    # =====================
    # Fair Value Gap
    # =====================

    bullish_fvg: bool = False
    bearish_fvg: bool = False

    bullish_fvg_price: float = 0.0
    bearish_fvg_price: float = 0.0

    # =====================
    # AI
    # =====================

    probability: int = 0

    confidence: str = ""

    smart_money_score: int = 0

    # =====================
    # Trade
    # =====================

    signal: str = ""

    entry: float = 0.0

    stop_loss: float = 0.0

    take_profit_1: float = 0.0
    take_profit_2: float = 0.0

    risk_reward: float = 0.0

    position_size: float = 0.0