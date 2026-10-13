import numpy as np


def crr_binomial_tree_price(
    spot: float,
    strike: float,
    expiry_years: float,
    rate: float,
    volatility: float,
    steps: int = 100,
    option_type: str = "CALL",
    exercise_style: str = "EUROPEAN",
    dividend_yield: float = 0.0,
) -> float:
    """
    Cox-Ross-Rubinstein (CRR) discrete binomial tree model.
    Supports both EUROPEAN and AMERICAN exercise styles.
    """
    if expiry_years <= 1e-6:
        return max(0.0, spot - strike if option_type.upper() == "CALL" else strike - spot)

    dt = expiry_years / float(steps)
    u = np.exp(volatility * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp((rate - dividend_yield) * dt) - d) / (u - d)
    df = np.exp(-rate * dt)

    is_call = option_type.upper() == "CALL"
    is_american = exercise_style.upper() == "AMERICAN"

    # Terminal asset prices at maturity
    # S_T = S * u^j * d^(N - j) for j = 0..N
    j = np.arange(steps + 1)
    st = spot * (u ** j) * (d ** (steps - j))

    # Payoff at expiration
    if is_call:
        values = np.maximum(0.0, st - strike)
    else:
        values = np.maximum(0.0, strike - st)

    # Backward induction
    for i in range(steps - 1, -1, -1):
        j_i = np.arange(i + 1)
        s_i = spot * (u ** j_i) * (d ** (i - j_i))
        continuation_value = df * (p * values[1:] + (1.0 - p) * values[:-1])

        if is_american:
            intrinsic_value = np.maximum(0.0, s_i - strike if is_call else strike - s_i)
            values = np.maximum(continuation_value, intrinsic_value)
        else:
            values = continuation_value

    return round(float(values[0]), 4)
