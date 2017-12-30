"""
Runs the breakout strategy over the market data
"""

class Breakout():
    """
    Runs the breakout strategy over the market data
    """
    def find_breakout(self, historical_data, breakout_threshold=.75):
        """
        Finds breakout based on how close the High was to Closing and Low to Opening
        """
        hit = 0
        for data_period in historical_data:
            if (data_period['C'] == data_period['H']) and (data_period['O'] == data_period['L']):
                hit += 1

        percent_positive_trend = hit / len(historical_data)
        if percent_positive_trend >= breakout_threshold:
            is_breaking_out = True
        else:
            is_breaking_out = False
        return percent_positive_trend, is_breaking_out
