def get_closing_prices(coin_pair, period, unit):
    """
    Returns closing prices within a specified time frame for a coin pair
    :type coin_pair: str
    :type period: str
    :type unit: int
    :return: Array of closing prices
    """

    historical_data = BITTREX_CLIENT.get_historical_data(coin_pair, period, unit)
    closing_prices = []
    for data_point in historical_data:
        closing_prices.append(data_point['C'])
    return closing_prices
