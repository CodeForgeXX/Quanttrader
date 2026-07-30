from src.core.analysis_builder import AnalysisBuilder

from src.ai.smart_money import SmartMoneyEngine
from src.ai.signal_ai import SignalAI
from src.ai.entry_engine import EntryEngine

from src.ai.probability_engine import ProbabilityEngine
from src.ai.confidence_engine import ConfidenceEngine
from src.ai.risk_manager import RiskManager
from src.ai.position_sizer import PositionSizer


class SignalGenerator:

    def __init__(self):

        self.builder = AnalysisBuilder()

        self.smart_money = SmartMoneyEngine()

        self.signal_ai = SignalAI()

        self.entry_engine = EntryEngine()

        self.probability = ProbabilityEngine()

        self.confidence = ConfidenceEngine()

        self.risk = RiskManager()

        self.position = PositionSizer()

    def generate(self, symbol, df):

        market = self.builder.build(symbol, df)

        market = self.smart_money.analyze(market)

        market = self.signal_ai.generate(market)

        market = self.probability.calculate(market)

        market = self.confidence.calculate(market)

        market = self.entry_engine.calculate(market)

        market = self.risk.calculate(market)

        market = self.position.calculate(market)

        return market