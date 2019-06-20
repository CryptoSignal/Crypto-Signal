""" Runs the default analyzer, which performs two functions...
1. Output the signal information to the prompt.
2. Notify users when a threshold is crossed.
"""

import json
import traceback
from copy import deepcopy

import structlog
from ccxt import ExchangeError
from tenacity import RetryError

from analysis import StrategyAnalyzer
from outputs import Output
from symbol import except_clause
import numpy as np
from collections import defaultdict
import traceback

import sys
from _ast import Or

class Behaviour():
    """Default analyzer which gives users basic trading information.
    """

    def __init__(self, config, exchange_interface, notifier):
        """Initializes DefaultBehaviour class.

        Args:
            indicator_conf (dict): A dictionary of configuration for this analyzer.
            exchange_interface (ExchangeInterface): Instance of the ExchangeInterface class for
                making exchange queries.
            notifier (Notifier): Instance of the notifier class for informing a user when a
                threshold has been crossed.
        """
        self.logger = structlog.get_logger()
        self.indicator_conf = config.indicators
        self.informant_conf = config.informants
        self.crossover_conf = config.crossovers
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = StrategyAnalyzer()
        self.notifier = notifier

        output_interface = Output()
        self.output = output_interface.dispatcher


    def run(self, market_pairs, output_mode):
        """The analyzer entrypoint

        Args:
            market_pairs (list): List of symbol pairs to operate on, if empty get all pairs.
            output_mode (str): Which console output mode to use.
        """

        self.logger.info("Starting default analyzer...")

        if market_pairs:
            self.logger.info("Found configured markets: %s", market_pairs)
        else:
            self.logger.info("No configured markets, using all available on exchange.")

        market_data = self.exchange_interface.get_exchange_markets(markets=market_pairs)

        self.logger.info("Using the following exchange(s): %s", list(market_data.keys()))

        self.truncateFile()
        new_result = self._test_strategies(market_data, output_mode)

        self.notifier.notify_all(new_result)

    def truncateFile(self):
        f = open(sys.argv[2],'r+')
        f.truncate()
        
    def _test_strategies(self, market_data, output_mode):
        """Test the strategies and perform notifications as required

        Args:
            market_data (dict): A dictionary containing the market data of the symbols to analyze.
            output_mode (str): Which console output mode to use.
        """
        f = open(sys.argv[2],'a')
        indicatorModes = sys.argv[3]
        indicatorTypeCoinMap = defaultdict(list)
        new_result = dict()
        for exchange in market_data:
            if exchange not in new_result:
                new_result[exchange] = dict()

            for market_pair in market_data[exchange]:
                if market_pair not in new_result[exchange]:
                    new_result[exchange][market_pair] = dict()

                new_result[exchange][market_pair]['indicators'] = self._get_indicator_results(
                    exchange,
                    market_pair
                )

                new_result[exchange][market_pair]['informants'] = self._get_informant_results(
                    exchange,
                    market_pair
                )
                
                band_flag_waiver = False
                di_flag_waiver = False
                try:          
                    
                    upperband = new_result[exchange][market_pair]['informants']['bollinger_bands'][0]['result']['upperband'] ;
                    middleband = new_result[exchange][market_pair]['informants']['bollinger_bands'][0]['result']['middleband'] ;
                    lowerband = new_result[exchange][market_pair]['informants']['bollinger_bands'][0]['result']['lowerband'] ;
                    low = new_result[exchange][market_pair]['informants']['ohlcv'][0]['result']['low'] ;
                    close = new_result[exchange][market_pair]['informants']['ohlcv'][0]['result']['close'] ;
                    high = new_result[exchange][market_pair]['informants']['ohlcv'][0]['result']['high'] ;
                    plus_di = new_result[exchange][market_pair]['indicators']['plus_di'][0]['result']['plus_di'] ;
                    minus_di = new_result[exchange][market_pair]['indicators']['minus_di'][0]['result']['minus_di'] ;
                    delta_di = plus_di - minus_di
                    macd = new_result[exchange][market_pair]['indicators']['macd'][0]['result']['macd'];
                    macd_signal = new_result[exchange][market_pair]['indicators']['macd'][0]['result']['macdsignal'];
                    delta_macd = new_result[exchange][market_pair]['indicators']['macd'][0]['result']['macdhist'];
                    ema = new_result[exchange][market_pair]['informants']['ema'][0]['result'];
                    kt = new_result[exchange][market_pair]['indicators']['kdj'][0]['result']['k'];
                    dt = new_result[exchange][market_pair]['indicators']['kdj'][0]['result']['d'];
                    jt = new_result[exchange][market_pair]['indicators']['kdj'][0]['result']['j'];
                
                    #core algorithm 1:
#                     if (len(upperband) != 0) and (len(middleband) != 0):
#                         delta_close_middleband = close - middleband;
#                         delta_high_upperband = high - upperband;
#                     else:
#                         band_flag_waiver = True;
#                     
#                     if (len(plus_di)) and (len(minus_di)):
#                         delta_di = plus_di - minus_di;
#                         incre_seq = self._lis(delta_di.values.tolist())
#                     else:
#                         di_flag_waiver = True
# 
#                     if (output_mode in self.output 
#                        and (di_flag_waiver
#                             or (len(delta_di)>0
#                                 and delta_di.iloc[-1] > 0
# #                                 and self._hasMinusBefore(delta_di)
#                                 ) 
#                            )
#                        and (band_flag_waiver
#                             or (len(delta_close_middleband)>0
#                                 and len(delta_close_middleband)>0  
#                                 and delta_close_middleband.iloc[-1] > 0 
#                                 and (delta_high_upperband.iloc[-1] < 0 
#                                       or self._hasMinusBefore(delta_close_middleband, self.informant_conf["bollinger_bands"])
#                                     )
#                                 )) 
#                         ):
#                         output_data = deepcopy(new_result[exchange][market_pair])
#                         print(
#                             exchange,
#                             self.output[output_mode](output_data, market_pair, exchange),
#                             end=''
#                         )
                        ##################################################
                        
                    #core algorithm 2:
                          
                    # goldenFork
                    intersectionValueAndMin = [0,0]
                    goldenForkMacd = (
                        
                        (delta_macd[len(delta_macd)-1] >= 0  and delta_macd[len(delta_macd)-2] <= 0 
                         and self.isTheIntersectionPointCloseToBePositive(macd, macd_signal, 1, intersectionValueAndMin)) or
                                  
                        (delta_macd[len(delta_macd)-1] >= 0  and delta_macd[len(delta_macd)-2] >= 0 and delta_macd[len(delta_macd)-3] <= 0 
                         and self.isTheIntersectionPointCloseToBePositive(macd, macd_signal, 2, intersectionValueAndMin)) or
                        
                        (delta_macd[len(delta_macd)-1] >= 0  and delta_macd[len(delta_macd)-2] >= 0 and delta_macd[len(delta_macd)-3] >= 0 
                         and delta_macd[len(delta_macd)-4] <= 0 
                         and self.isTheIntersectionPointCloseToBePositive(macd, macd_signal, 3, intersectionValueAndMin))
                    )
                    
                    #flatMacd
#                     flatMacd = (self.lastNMacdsArePositive(delta_macd, macd, 7))

                    macdVolumeMinusIsDecreased = False  
                    (macdVolumeMinus,min) = self.lastNMinusMacdVolume(delta_macd[0:len(delta_macd)-1])
                    if( len(macdVolumeMinus) != 0 and self.lastNMinusDecreased(macdVolumeMinus,min) ):
                        macdVolumeMinusIsDecreased = True
                    
                    #goldenForkKdj
                    len_k = len(kt)
                    len_d = len(dt)
                    len_j = len(jt)
                    goldenForkKdj = (
                        ((dt[len_d-2] >= kt[len_k-2]) and (kt[len_k-2] >= jt[len_j-2]))  
                        and 
                        ((dt[len_d-1] <= kt[len_k-1]) and (kt[len_k-1] <= jt[len_j-1]))  
                    )
                    
                    #dmi
                    lastNDMIIsPositive = goldenForkKdj and (self.lastNDMIIsPositive(delta_di, 2) or self.lastNDMIIsPositive(delta_di, 3) or self.lastNDMIIsPositive(delta_di, 4)) 
                    
                    #macdBottomDivergence
                    #input: data
                    #output: boolean
                    #detectBottomDivergence(detectMacdNegativeSlots(data))
                    macdBottomDivergence = delta_macd[len(delta_macd)-1] <= 0 and self.detectBottomDivergence(delta_macd, low, self.detectLastMacdNegativeSlots(delta_macd))

                    #bollCross
                    bollCross = False
                    if (len(middleband) != 0):
                        delta_close_middleband = close - middleband;
                        delta_low_middleband = low - middleband;
                        if ((delta_close_middleband.iloc[-1] > 0 and delta_low_middleband.iloc[-1] < 0) or
                            (delta_close_middleband.iloc[-2] > 0 and delta_low_middleband.iloc[-2] < 0) 
                            ):
                            bollCross = True
                    
                    #narrowedBoll
#                     (narrowedBoll, test_arr) = self.lastNBoolIsNarrowed((upperband/lowerband)**10, 5) # counts of narrowed points

########################################Filter coins by indicators
                    if(indicatorModes == 'easy'):
                        if (goldenForkKdj):
                            self.printResult(new_result, exchange, market_pair, output_mode, "kdj金叉信号", indicatorTypeCoinMap)
                        
                        if (goldenForkMacd):
                            self.printResult(new_result, exchange, market_pair, output_mode, "macd金叉信号", indicatorTypeCoinMap)
                        
                    if(indicatorModes == 'custom'):
                        if (goldenForkMacd):
                            self.printResult(new_result, exchange, market_pair, output_mode, ("0轴上:" if intersectionValueAndMin[0]>0 else "") + "macd金叉信号" + ":"
                                              + (str(round(intersectionValueAndMin[0],5)) + ":" +str(round(intersectionValueAndMin[1],5)) + ":" + str(round(intersectionValueAndMin[0]/intersectionValueAndMin[1], 2))
                                                ), indicatorTypeCoinMap
                                            )
                        
                        if (lastNDMIIsPositive):
                            self.printResult(new_result, exchange, market_pair, output_mode, "DMI", indicatorTypeCoinMap)
                            
                        if (goldenForkKdj):
                            self.printResult(new_result, exchange, market_pair, output_mode, "kdj金叉信号", indicatorTypeCoinMap)
                        
                        if (macdBottomDivergence):
                            self.printResult(new_result, exchange, market_pair, output_mode, "macd底背离", indicatorTypeCoinMap)
                            
#                         if (narrowedBoll):
#                             self.printResult(new_result, exchange, market_pair, output_mode, "narrowedBoll:" + str(test_arr), indicatorTypeCoinMap)
                        
                        if (goldenForkKdj and goldenForkMacd):
                            self.printResult(new_result, exchange, market_pair, output_mode, "kdj金叉信号|macd金叉信号", indicatorTypeCoinMap)
                            
                        if (goldenForkKdj and lastNDMIIsPositive):
                            self.printResult(new_result, exchange, market_pair, output_mode, "kdj金叉信号|DMI", indicatorTypeCoinMap)
                                                
                        if (bollCross):
                            self.printResult(new_result, exchange, market_pair, output_mode, "布林中轨信号", indicatorTypeCoinMap)
                            
#                     if (bollCross):
#                         self.printResult(new_result, exchange, market_pair, output_mode, "bollCrossUp")
                        
#                     if (flatMacd):
#                         self.printResult(new_result, exchange, market_pair, output_mode, "flatMacd")
                        
#                     if (macdVolumeMinusIsDecreased):
#                         self.printResult(new_result, exchange, market_pair, output_mode, "macdVolumeMinusIsDecreased")
######################################################        
                except Exception as e:
                    print("An exception occurred for " + market_pair + ":" + exchange)
                    print(e)
                    traceback.print_exc()
                
        #write everything to the email
        for indicator in indicatorTypeCoinMap:
            f.write(indicator + "\n");
            for coin in indicatorTypeCoinMap[indicator]:
                f.write("    币种/交易对:" + coin.replace('/','') + '\n' );
        f.close();
        
        # Print an empty line when complete
        return new_result

###############################################################
    #Test: a=[1,2,3,4,5,6,-1,-2]
    def detectLastMacdNegativeSlots(self, macd):
        flag = False;
        for i in range(len(macd)-1, -1, -1):
            if (macd[i] > 0):
                if(flag == True):
                    return i+1;
            elif (flag == False):
                flag = True;
                
    def getIndexOfMacdValley(self, macd, start):
        index = start
        minIndex = start
        min = macd[start]
        for value in macd[start:]:
            if(min > value):
                min = value;
                minIndex = index
            index = index + 1
        return minIndex
    
    def detectBottomDivergence(self, macd, data, start):
        minIndex = self.getIndexOfMacdValley(macd, start)
        min = data[(minIndex-len(macd))]
        loc = minIndex
        for value in data[(minIndex-len(macd)):]:
            if(value < min):
#                 print("(((((" + str(start))
#                 print("......" + str(minIndex))
#                 print("<<<<<<" + str(loc))
#                 print(str(value) + "====" + str(min))
                return True;
#             print("<<<<<<" + str(value) + "<<<" + str(loc))
            loc = loc + 1
        return False;
 ################################################################
    
    def isTheIntersectionPointCloseToBePositive(self, macd, macd_signal, n, intersectionValueAndMin):
        return self.calIntersectionPointRate(self.GetIntersectPointofLines(self.organizeDataPoint(macd, macd_signal, n))[0], macd, intersectionValueAndMin) is not None ;
    
    def organizeDataPoint(self, macd, macd_signal, n):
        return (macd[len(macd)-1-n], 1, macd[len(macd)-n], 2, macd_signal[len(macd_signal)-1-n], 1, macd_signal[len(macd_signal)-n], 2);
    
    def calIntersectionPointRate(self, intersectionValue, macd, intersectionValueAndMin): #intersectionRate
        (result, min) = self.lastNMinusMacdVolume(macd)
        intersectionValueAndMin[0] = intersectionValue;
        intersectionValueAndMin[1] = min;
        return intersectionValueAndMin;
       
    def GeneralEquation(self, first_x,first_y,second_x,second_y):
        A=second_y-first_y
        B=first_x-second_x
        C=second_x*first_y-first_x*second_y
        return A,B,C

    def GetIntersectPointofLines(self, vector):
        x1 = vector[0]
        y1 = vector[1] 
        x2 = vector[2] 
        y2 = vector[3] 
        x3 = vector[4] 
        y3 = vector[5] 
        x4 = vector[6] 
        y4 = vector[7] 
        A1,B1,C1 = self.GeneralEquation(x1,y1,x2,y2)
        A2, B2, C2 = self.GeneralEquation(x3,y3,x4,y4)
        m=A1*B2-A2*B1
        if m==0:
            print("no intersection")
        else:
            x=(C2*B1-C1*B2)/m
            y=(C1*A2-C2*A1)/m
        return x,y

    def lastNBoolIsNarrowed(self, delta_boll,n):
        test_arr = delta_boll[0-n:];
        for x in test_arr:
            if(x > 5.0): #narrowed area
                return (False, test_arr);
        return (True, test_arr);
    
    def lastNDMIIsPositive(self, delta_dmi,n):
        test_arr = delta_dmi[0-n:];
        theOneBefore = delta_dmi[len(delta_dmi)-n-1];
        for x in test_arr:
            if(x < 0):
                return False;
            
        return (theOneBefore < 0);
        
    def printResult(self, new_result, exchange, market_pair, output_mode, criteriaType, indicatorTypeCoinMap):
        output_data = deepcopy(new_result[exchange][market_pair])
        print(
                                exchange,
                                criteriaType,
                                self.output[output_mode](output_data, criteriaType, market_pair, exchange, indicatorTypeCoinMap),
                                end=''
            )
    
    def lastNMacdsArePositive(self, delta_macd, macd, n):
        (result, min) = self.lastNMinusMacdVolume(macd)
        test_arr = delta_macd[0-n:];
        theOneBefore = delta_macd[len(delta_macd)-n-1];
        for x in test_arr:
            if(x < 0 or (abs(x/min) >= 0.3)): #the rate of macd value divided by the megative highest macd value is less than 0.3
                return False;
            
        return True;
        
    def lastNMinusDecreased(self, delta_macd, min):
        for i in range(len(delta_macd)):
            if(delta_macd[i] == min and i != 0):
                return True;
            else:
                return False;
    
    def lastNMinusMacdVolume(self, delta_macd):
        result = []
        min = 0
        negativeStarted = False
        for x in reversed(delta_macd):
            if(x <= 0):
                negativeStarted = True
                if(x < min):
                    min = x
                result.append(x)
            elif negativeStarted: #always return from here
                return (result, min)
        return (result, min)
    
    def _hasMinusBefore(self, arr, informant):
        n = len(arr)
        period = informant[0]["candle_period"]
        if period == '1d':
            N = 10
        elif period == '1w':
            N = 3
        else:
            N = 10
        try:
            for index in range(n-1, n-1-N, -1):
                if arr[index] <= 0:
                    return True;
            return False;
        except Exception as e:         
            print("An exception occurred:" + str(e))
    
    def _lis(self, arr):
        n = len(arr)
        m = [0]*n
        for x in range(n-2,-1,-1):
            for y in range(n-1,x,-1):
                if arr[x] < arr[y] and m[x] <= m[y]:
                    m[x] += 1
            max_value = max(m)
            result = []
            for i in range(n):
                if m[i] == max_value:
                    result.append(arr[i])
                    max_value -= 1
        return result
     
 
    def _get_indicator_results(self, exchange, market_pair):
        """Execute the indicator analysis on a particular exchange and pair.

        Args:
            exchange (str): The exchange to get the indicator results for.
            market_pair (str): The pair to get the market pair results for.

        Returns:
            list: A list of dictinaries containing the results of the analysis.
        """

        indicator_dispatcher = self.strategy_analyzer.indicator_dispatcher()
        results = { indicator: list() for indicator in self.indicator_conf.keys() }
        historical_data_cache = dict()

        for indicator in self.indicator_conf:
            if indicator not in indicator_dispatcher:
                self.logger.warn("No such indicator %s, skipping.", indicator)
                continue

            for indicator_conf in self.indicator_conf[indicator]:
                if indicator_conf['enabled']:
                    candle_period = indicator_conf['candle_period']
                else:
                    self.logger.debug("%s is disabled, skipping.", indicator)
                    continue

                if candle_period not in historical_data_cache:
                    historical_data_cache[candle_period] = self._get_historical_data(
                        market_pair,
                        exchange,
                        candle_period
                    )

                if historical_data_cache[candle_period]:
                    analysis_args = {
                        'historical_data': historical_data_cache[candle_period],
                        'signal': indicator_conf['signal'],
                        'hot_thresh': indicator_conf['hot'],
                        'cold_thresh': indicator_conf['cold']
                    }

                    if 'period_count' in indicator_conf:
                        analysis_args['period_count'] = indicator_conf['period_count']

                    results[indicator].append({
                        'result': self._get_analysis_result(
                            indicator_dispatcher,
                            indicator,
                            analysis_args,
                            market_pair
                        ),
                        'config': indicator_conf
                    })
        return results


    def _get_informant_results(self, exchange, market_pair):
        """Execute the informant analysis on a particular exchange and pair.

        Args:
            exchange (str): The exchange to get the indicator results for.
            market_pair (str): The pair to get the market pair results for.

        Returns:
            list: A list of dictinaries containing the results of the analysis.
        """

        informant_dispatcher = self.strategy_analyzer.informant_dispatcher()
        results = { informant: list() for informant in self.informant_conf.keys() }
        historical_data_cache = dict()

        for informant in self.informant_conf:
            if informant not in informant_dispatcher:
                self.logger.warn("No such informant %s, skipping.", informant)
                continue

            for informant_conf in self.informant_conf[informant]:
                if informant_conf['enabled']:
                    candle_period = informant_conf['candle_period']
                else:
                    self.logger.debug("%s is disabled, skipping.", informant)
                    continue

                if candle_period not in historical_data_cache:
                    historical_data_cache[candle_period] = self._get_historical_data(
                        market_pair,
                        exchange,
                        candle_period
                    )

                if historical_data_cache[candle_period]:
                    analysis_args = {
                        'historical_data': historical_data_cache[candle_period]
                    }

                    if 'period_count' in informant_conf:
                        analysis_args['period_count'] = informant_conf['period_count']
                   
                    results[informant].append({
                        'result': self._get_analysis_result(
                            informant_dispatcher,
                            informant,
                            analysis_args,
                            market_pair
                        ),
                        'config': informant_conf
                    })

        return results


    def _get_crossover_results(self, new_result):
        """Execute crossover analysis on the results so far.

        Args:
            new_result (dict): A dictionary containing the results of the informant and indicator
                analysis.

        Returns:
            list: A list of dictinaries containing the results of the analysis.
        """

        crossover_dispatcher = self.strategy_analyzer.crossover_dispatcher()
        results = { crossover: list() for crossover in self.crossover_conf.keys() }

        for crossover in self.crossover_conf:
            if crossover not in crossover_dispatcher:
                self.logger.warn("No such crossover %s, skipping.", crossover)
                continue

            for crossover_conf in self.crossover_conf[crossover]:
                if not crossover_conf['enabled']:
                    self.logger.debug("%s is disabled, skipping.", crossover)
                    continue
                
                key_indicator = new_result[crossover_conf['key_indicator_type']][crossover_conf['key_indicator']][crossover_conf['key_indicator_index']]
                crossed_indicator = new_result[crossover_conf['crossed_indicator_type']][crossover_conf['crossed_indicator']][crossover_conf['crossed_indicator_index']]

                dispatcher_args = {
                    'key_indicator': key_indicator['result'],
                    'key_signal': crossover_conf['key_signal'],
                    'key_indicator_index': crossover_conf['key_indicator_index'],
                    'crossed_indicator': crossed_indicator['result'],
                    'crossed_signal': crossover_conf['crossed_signal'],
                    'crossed_indicator_index': crossover_conf['crossed_indicator_index']
                }

                results[crossover].append({
                    'result': crossover_dispatcher[crossover](**dispatcher_args),
                    'config': crossover_conf
                })
        return results


    def _get_historical_data(self, market_pair, exchange, candle_period):
        """Gets a list of OHLCV data for the given pair and exchange.

        Args:
            market_pair (str): The market pair to get the OHLCV data for.
            exchange (str): The exchange to get the OHLCV data for.
            candle_period (str): The timeperiod to collect for the given pair and exchange.

        Returns:
            list: A list of OHLCV data.
        """

        historical_data = list()
        try:
            historical_data = self.exchange_interface.get_historical_data(
                market_pair,
                exchange,
                candle_period
            )
        except RetryError:
            self.logger.error(
                'Too many retries fetching information for pair %s, skipping',
                market_pair
            )
        except ExchangeError:
            self.logger.error(
                'Exchange supplied bad data for pair %s, skipping',
                market_pair
            )
        except ValueError as e:
            self.logger.error(e)
            self.logger.error(
                'Invalid data encountered while processing pair %s, skipping',
                market_pair
            )
            self.logger.debug(traceback.format_exc())
        except AttributeError:
            self.logger.error(
                'Something went wrong fetching data for %s, skipping',
                market_pair
            )
            self.logger.debug(traceback.format_exc())
        return historical_data


    def _get_analysis_result(self, dispatcher, indicator, dispatcher_args, market_pair):
        """Get the results of performing technical analysis

        Args:
            dispatcher (dict): A dictionary of functions for performing TA.
            indicator (str): The name of the desired indicator.
            dispatcher_args (dict): A dictionary of arguments to provide the analyser
            market_pair (str): The market pair to analyse

        Returns:
            pandas.DataFrame: Returns a pandas.DataFrame of results or an empty string.
        """

        try:
            results = dispatcher[indicator](**dispatcher_args)
        except TypeError:
            self.logger.info(
                'Invalid type encountered while processing pair %s for indicator %s, skipping',
                market_pair,
                indicator
            )
            self.logger.info(traceback.format_exc())
            results = str()
        return results
