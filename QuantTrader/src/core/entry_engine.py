class EntryEngine:

    def init(self):
        pass

    def calculate(self, market):

        if market.signal == "BUY":

            market.entry = market.price

            if market.swing_lows:
                market.stop_loss = market.swing_lows[-1]
            else:
                market.stop_loss = market.price * 0.98

            risk = market.entry - market.stop_loss

            market.take_profit_1 = market.entry + risk
            market.take_profit_2 = market.entry + risk * 2

        elif market.signal == "SELL":

            market.entry = market.price

            if market.swing_highs:
                market.stop_loss = market.swing_highs[-1]
            else:
                market.stop_loss = market.price * 1.02

            risk = market.stop_loss - market.entry

            market.take_profit_1 = market.entry - risk
            market.take_profit_2 = market.entry - risk * 2

        return market