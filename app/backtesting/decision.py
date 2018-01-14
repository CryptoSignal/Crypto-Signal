

class Decision(object):
    def __init__(self, indicators):
        self.indicators = indicators

    def should_buy(self, buy_strategy):
        for indicator, body in buy_strategy.items():

            comparator, value = body['comparator'], body['value']

            if not isinstance(value, (int, float)):
                value = self.indicators[value]

            if comparator == 'LT':
                if self.indicators[indicator] >= value:
                    return False

            elif comparator == 'EQ':
                if self.indicators[indicator] != value:
                    return False

            elif comparator == 'GT':
                if self.indicators[indicator] <= value:
                    return False

        return True

    def should_sell(self, sell_strategy):
        for indicator, body in sell_strategy.items():

            comparator, value = body['comparator'], body['value']

            if not isinstance(value, (int, float)):
                value = self.indicators[value]

            if comparator == 'LT':
                if self.indicators[indicator] >= value:
                    return False

            elif comparator == 'EQ':
                if self.indicators[indicator] != value:
                    return False

            elif comparator == 'GT':
                if self.indicators[indicator] <= value:
                    return False

        return True
