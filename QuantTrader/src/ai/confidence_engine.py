class ConfidenceEngine:

    def calculate(self, market):

        p = market.probability

        if p >= 90:
            market.confidence = "VERY HIGH"

        elif p >= 75:
            market.confidence = "HIGH"

        elif p >= 60:
            market.confidence = "MEDIUM"

        elif p >= 40:
            market.confidence = "LOW"

        else:
            market.confidence = "VERY LOW"

        return market