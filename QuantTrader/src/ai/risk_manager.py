class RiskManager:

    def calculate(self, market):

        market.risk_reward = 0.0

        if market.signal == "WAIT":
            return market

        if market.entry <= 0:
            return market

        if market.stop_loss <= 0:
            return market

        if market.take_profit_2 <= 0:
            return market

        if market.signal == "BUY":

            risk = market.entry - market.stop_loss
            reward = market.take_profit_2 - market.entry

        else:

            risk = market.stop_loss - market.entry
            reward = market.entry - market.take_profit_2

        if risk > 0:
            market.risk_reward = round(reward / risk, 2)

        return market