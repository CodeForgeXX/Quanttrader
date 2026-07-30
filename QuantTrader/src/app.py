from config.settings import SYMBOLS
from src.core.trading_engine import TradingEngine


def start():

    print("\n")
    print("=" * 70)
    print("               QuantTrader PRO X")
    print("=" * 70)
    print()

    engine = TradingEngine()

    for symbol in SYMBOLS:

        market = engine.analyze(symbol)

        if market is None:
            continue

        print("=" * 70)
        print(f"Analyzing {market.symbol}")
        print("=" * 70)

        print(f"SYMBOL        : {market.symbol}")
        print(f"PRICE         : {market.price:.4f}")

        print("\nTREND")
        print(f"Trend         : {market.trend}")
        print(f"Structure     : {market.structure}")
        print(f"BOS           : {market.bos}")
        print(f"CHOCH         : {market.choch}")

        print("\nSMART MONEY")
        print(f"Buy Liquidity : {market.buy_side_liquidity}")
        print(f"Sell Liquidity: {market.sell_side_liquidity}")
        print(f"Liquidity Grab: {market.liquidity_grab}")

        print("\nORDER BLOCK")
        print(f"Bullish OB    : {market.bullish_ob}")
        print(f"Bearish OB    : {market.bearish_ob}")
        print(f"OB Strength   : {market.ob_strength}")

        print("\nFAIR VALUE GAP")
        print(f"Bullish FVG   : {market.bullish_fvg}")
        print(f"Bearish FVG   : {market.bearish_fvg}")

        print("\nAI")
        print(f"Probability   : {market.probability}%")
        print(f"Confidence    : {market.confidence}")
        print(f"Score         : {market.smart_money_score}")

        print("\nTRADE")
        print(f"Signal        : {market.signal}")

        if market.entry > 0:
            print(f"Entry         : {market.entry:.4f}")
            print(f"Stop Loss     : {market.stop_loss:.4f}")
            print(f"Take Profit 1 : {market.take_profit_1:.4f}")
            print(f"Take Profit 2 : {market.take_profit_2:.4f}")
            print(f"Risk/Reward   : {market.risk_reward:.2f}")

        print("=" * 70)
        print()

    print("✅ System Ready")