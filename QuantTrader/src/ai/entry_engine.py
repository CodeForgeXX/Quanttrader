class EntryEngine:

    def calculate(self, market):

        # مقادیر پیش‌فرض
        market.entry = 0.0
        market.stop_loss = 0.0
        market.take_profit_1 = 0.0
        market.take_profit_2 = 0.0
        market.risk_reward = 0.0

        if market.signal == "BUY":

            market.entry = market.price

            # حدود ۱ درصد پایین‌تر
            market.stop_loss = market.price * 0.99

            risk = market.entry - market.stop_loss

            market.take_profit_1 = market.entry + (risk * 2)
            market.take_profit_2 = market.entry + (risk * 4)

            market.risk_reward = round(
                (market.take_profit_1 - market.entry) /
                (market.entry - market.stop_loss),
                2
            )

        elif market.signal == "SELL":

            market.entry = market.price

            # حدود ۱ درصد بالاتر
            market.stop_loss = market.price * 1.01

            risk = market.stop_loss - market.entry

            market.take_profit_1 = market.entry - (risk * 2)
            market.take_profit_2 = market.entry - (risk * 4)

            market.risk_reward = round(
                (market.entry - market.take_profit_1) /
                (market.stop_loss - market.entry),
                2
            )

        return market