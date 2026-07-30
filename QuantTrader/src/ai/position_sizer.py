class PositionSizer:

    def calculate(
        self,
        market,
        capital=1000,
        risk_percent=1,
    ):

        market.position_size = 0.0

        if market.signal == "WAIT":
            return market

        if market.entry <= 0:
            return market

        if market.stop_loss <= 0:
            return market

        risk_amount = capital * (risk_percent / 100)

        if market.signal == "BUY":

            stop_distance = market.entry - market.stop_loss

        else:

            stop_distance = market.stop_loss - market.entry

        if stop_distance <= 0:
            return market

        market.position_size = round(
            risk_amount / stop_distance,
            4,
        )

        return market