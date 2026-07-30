from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Base class for all exchange providers.
    """

    @abstractmethod
    def get_klines(
        self,
        symbol,
        interval,
        limit,
    ):
        pass

    @abstractmethod
    def get_symbols(self):
        pass

    @abstractmethod
    def get_ticker(self, symbol):
        pass