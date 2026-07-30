class PositionSize:

    def calculate(self, balance, risk_percent, stop_distance):

        risk_amount = balance * (risk_percent / 100)

        if stop_distance == 0:
            return 0

        position = risk_amount / stop_distance

        return round(position, 4)