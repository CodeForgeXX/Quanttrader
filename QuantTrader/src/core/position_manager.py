class PositionManager:

    def init(self):

        self.position = None

    def open_position(
        self,
        symbol,
        side,
        size,
        entry,
        stop_loss,
        take_profit,
    ):

        self.position = {
            "symbol": symbol,
            "side": side,
            "size": size,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
        }

        return self.position

    def close_position(self):

        self.position = None

    def has_position(self):

        return self.position is not None

    def get_position(self):

        return self.position