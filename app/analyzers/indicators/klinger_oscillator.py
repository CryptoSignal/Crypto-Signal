

import pandas
import os
import numpy as np
import matplotlib.pyplot as plt

class Klinger_oscillator():
    def analyze(self, historical_data):

        #dataframe = self.convert_to_dataframe(historical_data)
        dataframe = historical_data
        print(dataframe.tail())
        """
        Klinger Oscillator = 34 period EMA of VF - 55 period EMA of VF
            LEADING INDICATOR
            USE WITH STOCHASTIC OSCILLATOR
        -----
        VF (volume force) = volume* ABS(Temp) *trend*100
        Temp = 2*((dm/cm)-1)
        
        if (high+low+close)/3 > (high_1+low_1+close_1)/3
            Trend = +1 
        if < or =
            Trend = -1        
        
        dm = high - low
        
        
        CM[today] =     / CM[yesterday] + DM[today] IF  trend[today]==trend[yesterday]
                        \ DM[yesterday] + DM[today] IF  trend[today]!=trend[yesterday]
        
        if Trend = Trend_1
            cm = cm_1 + dm 
        if Trend =/= Trend_1
            cm = dm_1 + dm 
        -----
        EMA = (c*A)+(E*B)
        C = current period's VF
        A = 2/(X+1) where C is the moving average period(34 or 55)
        E = prior period's EMA
        B = 1-A
        ------
        chart
        KVO line = (fast EMA  - flow EMA) = 32periodEMA(vf) - 55periodEMA(vf)
            green
        signal line = 13 period EMA of KVO line
            red
        ====
        dm = daily measurement
        cm = cumulative measurement
        vf = volume force
        
        """


        dataframe['mean'] = dataframe[['high', 'low', 'close']].mean(axis=1)
        dataframe['trend'] = np.nan
        print('calculating trend')
        for index in range(1, (dataframe.shape[0])):
            if dataframe['mean'][index] > dataframe['mean'][index-1]:
                dataframe['trend'][index] = 1
            else:
                dataframe['trend'][index] = -1

            dataframe['dm'] = dataframe['high'][index] - dataframe['low'][index]
        dataframe['cm'] = np.nan
        print('calculating cm')
        for index in range(0, (dataframe.shape[0])):
            dataframe['cm_a'] = dataframe['dm'][index] + dataframe['dm'][index-1]
            if dataframe['trend'][index] == dataframe['trend'][index-1]:
                dataframe['cm'][index] = dataframe['cm'][index-1] + dataframe['dm'][index]
            else:
                dataframe['cm'][index] = dataframe['dm'][index] + dataframe['dm'][index-1]
        print('calculating')
        dataframe['vfema'] = np.nan
        dataframe['volumeforce'] = dataframe['volume'] * abs(2*((dataframe['dm']/dataframe['cm'])-1)) * dataframe['trend'] * 100
        dataframe['32ema'] = dataframe['volumeforce'].ewm(span=32, min_periods=0, adjust=False, ignore_na=True).mean()
        dataframe['55ema'] = dataframe['volumeforce'].ewm(span=55, min_periods=0, adjust=False, ignore_na=True).mean()
        dataframe['kvo'] = dataframe['32ema'] - dataframe['55ema']
        dataframe['vf'] = dataframe['32ema'] - dataframe['55ema']
        dataframe['vfema'] = dataframe['vf'].ewm(span=13, min_periods=0, adjust=False, ignore_na=True).mean()
        print(dataframe.head())
        print(dataframe.tail())
        dataframe.to_csv('klinger')
        print('finished calculations')
        return dataframe

    def create_chart(self, data):

        print('data:', data.tail())
        x = data.index
        y = data['vf']
        plt.plot(x, y)
        y1 = data['vfema']
        plt.plot(x, y1)
        plt.xlabel('x-axis')
        plt.ylabel('dates')
        plt.show()



if __name__ == '__main__':
    hist = pandas.read_csv(r'savefunctiondata')
    hist = hist.set_index(pandas.to_datetime(hist['datetime']))
    hist.drop('datetime', axis=1, inplace=True)
    ko = Klinger_oscillator()
    data = ko.analyze(historical_data=hist)
    ko.create_chart(data)