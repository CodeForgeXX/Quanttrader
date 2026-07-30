def calculate_position_size(balance, risk_percent, entry, stop):
    """
    Calculate position size (in units of the asset) and the dollar
    amount being risked, given an account balance, a risk percentage,
    and the distance between entry and stop-loss price.

    Returns a dict: {"position_size": float, "risk_amount": float}
    """

    risk_amount = balance * (risk_percent / 100)

    stop_distance = abs(entry - stop)

    if stop_distance == 0:
        return {"position_size": 0, "risk_amount": round(risk_amount, 2)}

    position_size = risk_amount / stop_distance

    return {
        "position_size": round(position_size, 4),
        "risk_amount": round(risk_amount, 2),
    }
