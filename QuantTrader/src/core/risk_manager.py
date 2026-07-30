from config.settings import (
    ACCOUNT_BALANCE,
    RISK_PERCENT,
)


class RiskManager:

    def init(self):

        self.balance = ACCOUNT_BALANCE
        self.risk_percent = RISK_PERCENT

    def calculate(self, entry, stop_loss):

        risk_amount = self.balance * (
            self.risk_percent / 100
        )

        risk_per_unit = abs(entry - stop_loss)

        if risk_per_unit == 0:
            return 0

        position_size = risk_amount / risk_per_unit

        return round(position_size, 4)