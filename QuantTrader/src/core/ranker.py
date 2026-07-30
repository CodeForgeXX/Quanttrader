from typing import List


class SignalRanker:

    def rank(self, markets) -> List:

        if not markets:
            return []

        buy = []
        sell = []
        wait = []

        for market in markets:

            score = (
                market.probability
                + market.smart_money_score
                + market.ob_strength
            )

            if market.signal == "BUY":
                buy.append((score, market))

            elif market.signal == "SELL":
                sell.append((score, market))

            else:
                wait.append((score, market))

        buy.sort(key=lambda x: x[0], reverse=True)
        sell.sort(key=lambda x: x[0], reverse=True)
        wait.sort(key=lambda x: x[0], reverse=True)

        result = []

        for _, market in buy:
            result.append(market)

        for _, market in sell:
            result.append(market)

        # اگر BUY یا SELL نبود،
        # سه WAIT قوی را نمایش بده
        if len(result) == 0:
            for _, market in wait[:3]:
                result.append(market)

        return result