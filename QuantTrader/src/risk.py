def calculate_position_size(
    balance,
    risk_percent,
    entry,
    stop,
):
    """
    Calculate position size based on account risk.
    """

    risk_amount = balance * (risk_percent / 100)

    stop_distance = abs(entry - stop)

    if stop_distance == 0:
        return {
            "position_size": 0,
            "risk_amount": 0,
        }

    position_size = risk_amount / stop_distance

    return {
        "position_size": round(position_size, 4),
        "risk_amount": round(risk_amount, 2),
    }