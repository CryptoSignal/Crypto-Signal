""" 
Squeeze Momentum Indicator

This indicator is based on this code: 
https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/

by LazyBear https://www.tradingview.com/u/LazyBear/

"""

import numpy as np
from analyzers.utils import IndicatorUtils


class SQZMOM(IndicatorUtils):
    def analyze(
        self,
        historical_data,
        signal=["is_hot"],
        hot_thresh=None,
        cold_thresh=None,
    ):
        """Performs a macd analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to macd
            hot_thresh (float, optional): Unused for this indicator
            cold_thresh (float, optional): Unused for this indicator

        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        df = self.convert_to_dataframe(historical_data)
        sqzmom = df.copy(deep=True)

        # parameter setup (default values in the original indicator)
        length = 20
        mult = 2
        length_KC = 20
        mult_KC = 1.5

        # calculate Bollinger Bands

        # moving average
        m_avg = df["close"].rolling(window=length).mean()
        # standard deviation
        m_std = df["close"].rolling(window=length).std(ddof=0)
        # upper Bollinger Bands
        df["upper_BB"] = m_avg + mult * m_std
        # lower Bollinger Bands
        df["lower_BB"] = m_avg - mult * m_std

        # calculate Keltner Channel

        # first we need to calculate True Range
        df["tr0"] = abs(df["high"] - df["low"])
        df["tr1"] = abs(df["high"] - df["close"].shift())
        df["tr2"] = abs(df["low"] - df["close"].shift())
        df["tr"] = df[["tr0", "tr1", "tr2"]].max(axis=1)
        # moving average of the TR
        range_ma = df["tr"].rolling(window=length_KC).mean()
        # upper Keltner Channel
        df["upper_KC"] = m_avg + range_ma * mult_KC
        # lower Keltner Channel
        df["lower_KC"] = m_avg - range_ma * mult_KC

        # check for 'squeeze'
        df["squeeze_on"] = (df["lower_BB"] > df["lower_KC"]) & (
            df["upper_BB"] < df["upper_KC"]
        )
        df["squeeze_off"] = (df["lower_BB"] < df["lower_KC"]) & (
            df["upper_BB"] > df["upper_KC"]
        )

        # calculate momentum value
        highest = df["high"].rolling(window=length_KC).max()
        lowest = df["low"].rolling(window=length_KC).min()
        m1 = (highest + lowest) / 2
        df["value"] = df["close"] - (m1 + m_avg) / 2
        fit_y = np.array(range(0, length_KC))
        df["value"] = (
            df["value"]
            .rolling(window=length_KC)
            .apply(
                lambda x: np.polyfit(fit_y, x, 1)[0] * (length_KC - 1)
                + np.polyfit(fit_y, x, 1)[1],
                raw=True,
            )
        )

        # entry point for long position:
        # 1. black cross becomes gray (the squeeze is released)
        long_cond1 = (df["squeeze_off"][-2] == False) & (
            df["squeeze_off"][-1] == True
        )
        # 2. bar value is positive => the bar is light green
        long_cond2 = df["value"][-1] > 0
        enter_long = long_cond1 and long_cond2

        # entry point for short position:
        # 1. black cross becomes gray (the squeeze is released)
        short_cond1 = (df["squeeze_off"][-2] == False) & (
            df["squeeze_off"][-1] == True
        )
        # 2. bar value is negative => the bar is light red
        short_cond2 = df["value"][-1] < 0
        enter_short = short_cond1 and short_cond2

        sqzmom["is_hot"] = False
        sqzmom["is_cold"] = False

        sqzmom.at[sqzmom.index[-1], "is_hot"] = enter_long
        sqzmom.at[sqzmom.index[-1], "is_cold"] = enter_short

        return sqzmom
