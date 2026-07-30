from src.models.analysis import MarketAnalysis
from src.indicators import ema

from src.ai.market_structure import MarketStructure
from src.ai.liquidity_engine import LiquidityEngine
from src.ai.order_block import OrderBlockEngine
from src.ai.fvg_engine import FVGEngine


class AnalysisBuilder:

    def __init__(self):

        self.market_structure = MarketStructure()
        self.liquidity = LiquidityEngine()
        self.order_block = OrderBlockEngine()
        self.fvg = FVGEngine()

    def build(self, symbol, df):

        closes = df["Close"]

        price = closes.iloc[-1]

        ema20 = ema(closes, 20).iloc[-1]
        ema50 = ema(closes, 50).iloc[-1]
        ema200 = ema(closes, 200).iloc[-1]

        volume = df["Volume"].iloc[-1]
        avg_volume = df["Volume"].tail(20).mean()

        # Market Structure
        structure = self.market_structure.analyze(df)

        # Liquidity
        liquidity = self.liquidity.analyze(
            df,
            structure["swing_highs"],
            structure["swing_lows"],
        )

        # Order Block
        order_block = self.order_block.analyze(
            df,
            structure["structure"],
            structure["swing_highs"],
            structure["swing_lows"],
        )

        # Fair Value Gap
        fvg = self.fvg.analyze(df)

        return MarketAnalysis(

            symbol=symbol,

            price=price,

            ema20=ema20,
            ema50=ema50,
            ema200=ema200,

            volume=volume,
            avg_volume=avg_volume,

            structure=structure["structure"],

            bos=structure["bos"],
            choch=structure["choch"],

            swing_highs=structure["swing_highs"],
            swing_lows=structure["swing_lows"],

            buy_side_liquidity=liquidity["buy_side"],
            sell_side_liquidity=liquidity["sell_side"],
            liquidity_grab=liquidity["liquidity_grab"],
            equal_highs=liquidity["equal_highs"],
            equal_lows=liquidity["equal_lows"],

            bullish_ob=order_block["bullish_ob"],
            bearish_ob=order_block["bearish_ob"],
            bullish_ob_price=order_block["bullish_ob_price"],
            bearish_ob_price=order_block["bearish_ob_price"],
            ob_strength=order_block["ob_strength"],
            mitigated=order_block["mitigated"],

            bullish_fvg=fvg["bullish_fvg"],
            bearish_fvg=fvg["bearish_fvg"],
            bullish_fvg_price=fvg["bullish_fvg_price"],
            bearish_fvg_price=fvg["bearish_fvg_price"],
        )