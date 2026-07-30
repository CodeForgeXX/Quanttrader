class RiskReward:

    def calculate(self, entry, stop_loss, take_profit):

        risk = abs(entry - stop_loss)

        reward = abs(take_profit - entry)

        if risk == 0:
            return 0

        return round(reward / risk, 2)