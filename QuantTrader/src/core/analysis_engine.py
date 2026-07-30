from src.ai.trend_engine import TrendEngine
from src.ai.probability_engine import ProbabilityEngine
from src.ai.confidence_engine import ConfidenceEngine


class AnalysisEngine:

    def __init__(self):

        self.trend = TrendEngine()
        self.probability = ProbabilityEngine()
        self.confidence = ConfidenceEngine()

    def analyze(
        self,
        price,
        ema20,
        ema50,
        ema200,
    ):

        trend = self.trend.analyze(
            price,
            ema20,
            ema50,
            ema200,
        )

        probability = self.probability.calculate(
            trend["score"],
            0,
            0,
            0,
            0,
        )

        confidence = self.confidence.calculate(
            probability["probability"]
        )

        return {
            "trend": trend["trend"],
            "trend_score": trend["score"],
            "probability": probability["probability"],
            "confidence": confidence["confidence"],
        }