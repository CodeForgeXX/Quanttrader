class CHoCHEngine:

    def __init__(self):
        pass

    def analyze(
        self,
        structure,
        bos,
    ):

        choch = False

        if structure == "UPTREND" and not bos:

            choch = True

        elif structure == "DOWNTREND" and not bos:

            choch = True

        return {

            "choch": choch
        }