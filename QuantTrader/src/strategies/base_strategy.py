from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    """

    @abstractmethod
    def analyze(self, data):
        """
        Analyze market data and return a signal.
        """
        pass