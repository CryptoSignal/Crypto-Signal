
"""
Decision encapsulates a boolean process that determines when to open and close a trade
"""
class Decision(object):
    def __init__(self, indicators):
        self.indicators = indicators


    '''
    Determines if we should buy given our buy strategies and our observed indicators

    @param buy_strategy: A dictionary of the form: {'<INDICATOR_NAME>': {
                                                        'comparator': '...',
                                                        'value': '...'
                                                        }
                                                    }
    <INDICATOR_NAME> can take values such as 'currentprice', 'rsi', 'sma9', or 'sma15' (for now)
    The value for the 'comparator' key can be either 'LT', 'EQ', or 'GT'.
    The value for the 'value' key can be either a number or the name of an indicator mentioned above.

    :returns True iff each indicator satisfies a comparision using it's 'comparator' value with its 'value' value. False otherwise
    '''
    def should_buy(self, buy_strategy):
        for indicator, body in buy_strategy.items():
            comparator, value = body['comparator'], body['value']

            if not isinstance(value, (int, float)):
                value = self.indicators[value]

            if comparator == 'LT':
                if self.indicators[indicator] >= value[0]:
                    return False

            elif comparator == 'EQ':
                if self.indicators[indicator] != value[0]:
                    return False

            elif comparator == 'GT':
                if self.indicators[indicator] <= value[0]:
                    return False

        return True

    '''
        Determines if we should sell given our sell strategies and our observed indicators

        @param sell_strategy: A dictionary of the form: {'<INDICATOR_NAME>': {
                                                            'comparator': '...',
                                                            'value': '...'
                                                            }
                                                        }
        <INDICATOR_NAME> can take values such as 'currentprice', 'rsi', 'sma9', or 'sma15' (for now)
        The value for the 'comparator' key can be either 'LT', 'EQ', or 'GT'.
        The value for the 'value' key can be either a number or the name of an indicator mentioned above.

        :returns True iff each indicator satisfies a comparision using it's 'comparator' value with its 'value' value. False otherwise
        '''
    def should_sell(self, sell_strategy):
        for indicator, body in sell_strategy.items():

            comparator, value = body['comparator'], body['value']

            if not isinstance(value, (int, float)):
                value = self.indicators[value]

            if comparator == 'LT':
                if self.indicators[indicator] >= value[0]:
                    return False

            elif comparator == 'EQ':
                if self.indicators[indicator] != value[0]:
                    return False

            elif comparator == 'GT':
                if self.indicators[indicator] <= value[0]:
                    return False

        return True
