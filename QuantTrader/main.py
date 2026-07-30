from config.settings import SYMBOLS
from src.core.trading_engine import TradingEngine
from src.core.ranker import SignalRanker


def start():

    print("\n")
    print("=" * 70)
    print("               QuantTrader PRO X")
    print("=" * 70)
    print()

    engine = TradingEngine()
    ranker = SignalRanker()

    markets = []

    for symbol in SYMBOLS:

        market = engine.analyze(symbol)

        if market is not None:
            markets.append(market)

    ranked = ranker.rank(markets)

    print("\n")
    print("=" * 70)
    print("               TOP TRADING SIGNALS")
    print("=" * 70)

    if len(ranked) == 0:

        print("No BUY / SELL signals found.")

    else:

        for i, market in enumerate(ranked, start=1):

            print("\n")
            print("=" * 70)
            print(f"#{i}  {market.symbol}")
            print("=" * 70)

            print(f"Signal        : {market.signal}")
            print(f"Probability   : {market.probability}%")
            print(f"Confidence    : {market.confidence}")
            print(f"Trend         : {market.trend}")
            print(f"Structure     : {market.structure}")

            print(f"Entry         : {market.entry:.4f}")
            print(f"Stop Loss     : {market.stop_loss:.4f}")
            print(f"Take Profit 1 : {market.take_profit_1:.4f}")
            print(f"Take Profit 2 : {market.take_profit_2:.4f}")
            print(f"Risk/Reward   : {market.risk_reward:.2f}")

    print("\n")
    print("✅ Scan Finished")


if __name__ == "__main__":
    start()