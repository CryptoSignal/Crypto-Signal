import numpy as np


class BacktestingIndicators(object):
    def __init__(self):
        pass

    @staticmethod
    def historical_moving_average(prices, period):
        ret = np.zeros(period)

        for i in range(period, len(prices)):
            ret = np.append(ret, float(sum(prices[i - period: i]) / period))

        return ret

    @staticmethod
    def historical_rsi(prices, period=14):
        deltas = np.diff(prices)
        seed = deltas[:period + 1]
        rsi_up = seed[seed >= 0].sum() / period
        rsi_down = -seed[seed < 0].sum() / period

        rsi = np.zeros_like(prices)
        rs = rsi_up / rsi_down
        rsi[:period] = 100. - 100. / (1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            rsi_up = (rsi_up * (period - 1) + upval) / period
            rsi_down = (rsi_down * (period - 1) + downval) / period
            rs = rsi_up / rsi_down
            rsi[i] = 100. - 100. / (1. + rs)

        if len(prices) > period:
            return rsi
        else:
            return 50  # output a neutral amount until enough prices in list to calculate rsi

    @staticmethod
    def historical_bollinger_bands(prices, period=21, k=2):
        sma = BacktestingIndicators.historical_moving_average(prices, period=21)

        uppers = np.zeros(period)
        lowers = np.zeros(period)

        for i in range(period, len(prices)):
            std_dev = np.std(prices[i - period: i])
            upper, lower = sma[i] + k * std_dev, sma[i] - k * std_dev
            uppers = np.append(uppers, upper)
            lowers = np.append(lowers, lower)

        return uppers, lowers