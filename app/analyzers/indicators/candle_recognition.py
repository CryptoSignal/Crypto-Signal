
import numpy
import pandas
import talib

from analyzers.utils import IndicatorUtils


class Candle_recognition(IndicatorUtils):
    def analyze(self, historical_data, signal, notification='hot', candle_check=1, hot_thresh=None, cold_thresh=None):
        """Performs an candle pattern analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            notification (string): whether you want 'hot' or 'cold' notification. Defaults to hot.
            signal (list, optional): The specific candles to check for.
            candle_check (int, optional): The periods to check (1 = check only last candle)
            hot_thresh (float, optional): Defaults to None.
            cold_thresh (float, optional): Defaults to None.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """
        dataframe = self.convert_to_dataframe(historical_data)

        open = dataframe['open']
        high = dataframe['high']
        low = dataframe['low']
        close = dataframe['close']

        candle_functions = {
            'two_crows': talib.CDLTRISTAR,
            'three_black_crows': talib.CDL3BLACKCROWS,
            'three_inside_up_down': talib.CDL3INSIDE,
            'three_line_strike': talib.CDL3LINESTRIKE,
            'thee_stars_in_the_south': talib.CDL3OUTSIDE,
            'three_advancing_white_soldiers': talib.CDL3WHITESOLDIERS,
            'abandoned_baby': talib.CDLABANDONEDBABY,
            'advance_block': talib.CDLADVANCEBLOCK,
            'belt_hold': talib.CDLADVANCEBLOCK,
            'breakaway': talib.CDLBREAKAWAY,
            'closing_marubozu': talib.CDLCLOSINGMARUBOZU,
            'concealing_baby_swallow': talib.CDLCONCEALBABYSWALL,
            'counterattack': talib.CDLCOUNTERATTACK,
            'dark_cloud_cover': talib.CDLDARKCLOUDCOVER,
            'doji': talib.CDLDOJI,
            'doji_star': talib.CDLDOJISTAR,
            'dragonfly_doji': talib.CDLDRAGONFLYDOJI,
            'engulfing_pattern': talib.CDLENGULFING,
            'evening_doji_star': talib.CDLEVENINGDOJISTAR,
            'evening_star': talib.CDLEVENINGSTAR,
            'gap_sidesidewhite': talib.CDLGAPSIDESIDEWHITE,
            'gravestone_doji': talib.CDLGRAVESTONEDOJI,
            'hammer': talib.CDLHAMMER,
            'hanging_man': talib.CDLHANGINGMAN,
            'harami_pattern': talib.CDLHARAMI,
            'harami_cross_patern': talib.CDLHARAMICROSS,
            'high_wave_candle': talib.CDLHIGHWAVE,
            'modified_hikkake_pattern': talib.CDLHIKKAKEMOD,
            'homing_pigeon': talib.CDLHOMINGPIGEON,
            'identical_three_crows': talib.CDLIDENTICAL3CROWS,
            'in_neck_pattern': talib.CDLINNECK,
            'inverted_hammer': talib.CDLINVERTEDHAMMER,
            'kicking': talib.CDLKICKING,
            'kicking_bb': talib.CDLKICKINGBYLENGTH,
            'ladder_bottom': talib.CDLLADDERBOTTOM,
            'long_legged_doji': talib.CDLLONGLEGGEDDOJI,
            'long_line_candle': talib.CDLLONGLINE,
            'marubozu': talib.CDLMARUBOZU,
            'matching_low': talib.CDLMATCHINGLOW,
            'mat_hold': talib.CDLMATHOLD,
            'morning_doji_star': talib.CDLMORNINGDOJISTAR,
            'morning_star': talib.CDLMORNINGSTAR,
            'on_neck_pattern': talib.CDLONNECK,
            'piercing_pattern': talib.CDLPIERCING,
            'rickshaw_man': talib.CDLRICKSHAWMAN,
            'risfall_three_methods': talib.CDLRISEFALL3METHODS,
            'seperating_lines': talib.CDLSEPARATINGLINES,
            'shooting_star': talib.CDLSHOOTINGSTAR,
            'short_line_candle': talib.CDLSHORTLINE,
            'spinning_top': talib.CDLSPINNINGTOP,
            'stalled_pattern': talib.CDLSTALLEDPATTERN,
            'stick_sandwich': talib.CDLSTICKSANDWICH,
            'takuri': talib.CDLTAKURI,
            'tasuki_gap': talib.CDLTASUKIGAP,
            'thrusting_pattern': talib.CDLTHRUSTING,
            'tristar_pattern': talib.CDLTRISTAR,
            'unique_three_river': talib.CDLUNIQUE3RIVER,
            'upside_gap_two_crows': talib.CDLUPSIDEGAP2CROWS,
            'xside_gap_three_methods': talib.CDLXSIDEGAP3METHODS
        }

        candles_values = pandas.DataFrame(index=dataframe.index)

        candle_args = {'open': open, 'high': high, 'low': low, 'close': close}
        for candle in signal:
            if candle in candle_functions.keys():
                candles_values[candle] = candle_functions[candle](
                    **candle_args)

        candles_values['is_hot'] = False
        candles_values['is_cold'] = False

        to_check = 0 - candle_check
        for candle in signal:
            if len(set(candles_values[candle].iloc[to_check:])) != 1:
                if notification == 'hot':
                    candles_values['is_hot'][-1] = True
                elif notification == 'cold':
                    candles_values['is_cold'][-1] = True

        for candle in signal:
            candles_values[candle] = candles_values[candle].astype(float)

        return candles_values
