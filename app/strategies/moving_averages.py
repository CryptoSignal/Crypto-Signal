def calculate_sma(coin_pair, period, unit):
    """
    Returns the Simple Moving Average for a coin pair
    """

    total_closing = sum(get_closing_prices(coin_pair, period, unit))
    return total_closing / period

def calculate_ema(coin_pair, period, unit):
    """
    Returns the Exponential Moving Average for a coin pair
    """

    closing_prices = get_closing_prices(coin_pair, period, unit)
    previous_ema = calculate_sma(coin_pair, period, unit)
    period_constant = 2 / (1 + period)
    current_ema = (closing_prices[-1] * period_constant) \
                  + (previous_ema * (1 - period_constant))
    return current_ema
