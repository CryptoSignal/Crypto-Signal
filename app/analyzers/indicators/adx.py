
import pandas
import os
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import table

class Adx():
    def analyze(self, historical_data):

        #dataframe = self.convert_to_dataframe(historical_data)
        dataframe = historical_data


        """
        strength of a trend
        ADX > 25 = strength
        ADX < 20 = weak or trendless
        
        +DI = [(smoothed+DM)/ATR] * 100
        -DI = [(smoothed-DM)/ATR] * 100
        ADX= ((prior_adx * 13) + current_adx)/14
        
        +DM(directional movement) = current high - previous high
        -DM = previous low - current low 
        
        smoothed +/- DM = sum(DM)over14periods - [(sum(DM)over14periods)/14] + currentDM
        ~~~~~~~~~~~~~~~~~~~~~~~~
        ATR = average true range
        
        calculate +DM,-DM and TR (true range) for each period. typically 14 periods are used
        +DM = current high - previous high
        -DM = previous low - current low
        IF current high - previous high > previous low - current low
            use +DM
        IF previous low - current low > current high - previous high
            use -DM
        TR is the greater of 
            current high - current low
            current high - previous close
            current low - previous close
        smooth the 14-period averages of
            +DM
            -DM
            TR
        TR formula below. Insert the -DM and +DM values to calculate the smoothed averages of those
        
        first 14TR = sum of first 14TR readings
        next 14TR value = first14TR - (prior14TR/14) + currentTR
        next, divide the smoothed +DM value by the smoothed TR value to get +DI
            multiply by 100
        divide the smoothed -DM value by the smoother TR value to get -DI
            multiply by 100
        the directional movement index(DX) is 
            +DI minus -DI, divided by the sum of +DI and -DI (all absolute values)
            multiply by 100
        to get ADX
            continue to calculate DX values for at least 14 periods. then smooth the results to get ADX.
            
        first ADX = sum 14 periods of DX/14
        after that, ADX = ((prior adx * 13)+current dx) / 14
        
        """

        data = self.TR(dataframe)
        data = self.DM(data)
        data = self.DI(data)
        data = self.ATR(data)
        data = self.ADX(data)



        return dataframe

    def TR(self, dataframe):
        """
        TR is the greater of
            current high - current low
            current high - previous close
            current low - previous close
        :param dataframe:
        :return:
        """
        dataframe['tr'] = np.nan
        dataframe['tr'][0] = abs(dataframe['high'][0] - dataframe['low'][0])
        for index in range(1, dataframe.shape[0]):
            x = dataframe['high'][index] - dataframe['close'][index]
            y = abs(dataframe['high'][index] - dataframe['close'][index-1])
            z = abs(dataframe['low'][index] - dataframe['close'][index-1])
            dataframe['tr'][index] = max(x, y, z)

        return dataframe


    def DM(self, dataframe):
        """
        +DM = current high - previous high
        -DM = previous low - current low
        IF current high - previous high > previous low - current low
            use +DM
        IF previous low - current low > current high - previous high
            use -DM
        :param dataframe:
        :return:
        """
        dataframe['dm'] = np.nan
        dataframe['pdm'] = np.nan
        dataframe['ndm'] = np.nan
        period = 14

        for index in range(1, dataframe.shape[0]):
            up_move = dataframe['high'][index] - dataframe['high'][index-1]
            down_move = dataframe['low'][index-1] - dataframe['low'][index]

            if up_move > down_move and up_move > 0:
                dataframe['pdm'][index] = up_move
            else:
                dataframe['pdm'][index] = 0
            if down_move > up_move and down_move > 0:
                dataframe['ndm'][index] = down_move
            else:
                dataframe['ndm'][index] = 0

        dataframe['pdmsmooth'] = np.nan
        dataframe['ndmsmooth'] = np.nan

        dataframe['pdmsmooth'][period-1] = dataframe['pdm'][0:period].sum() / period
        dataframe['ndmsmooth'][period - 1] = dataframe['ndm'][0:period].sum() / period

        for index in range(period, dataframe.shape[0]):
            dataframe['pdmsmooth'][index] = (dataframe['pdm'][index-1] - (dataframe['pdmsmooth'][index-1]/period)) + dataframe['pdmsmooth'][index-1]
            dataframe['ndmsmooth'][index] = (dataframe['ndm'][index - 1] - (dataframe['ndmsmooth'][index-1] / period)) + dataframe['ndmsmooth'][index-1]
        return dataframe


    def DI(self, dataframe):
        """
        +DI = [(smoothed+DM)/ATR] * 100
        -DI = [(smoothed-DM)/ATR] * 100
        """
        dataframe['pdi'] = np.nan
        dataframe['ndi'] = np.nan
        for index in range(0, dataframe.shape[0]):
            dataframe['pdi'][index] = (dataframe['pdmsmooth'][index] / dataframe['tr'][index]) * 100
            dataframe['ndi'][index] = (dataframe['ndmsmooth'][index] / dataframe['tr'][index]) * 100

        return dataframe


    def ATR(self, dataframe):
        """
        WILDER'S SMOOTHING METHOD
        ATR = a*TR + (1-a)* ATR_1
        a = (1/n)
        """
        period = 14
        dataframe['atr'] = np.nan

        dataframe['atr'][period-1] = dataframe['tr'][0:period].sum() / period

        for index in range(period, dataframe.shape[0]):
            dataframe['atr'][index] = ((dataframe['atr'][index-1] * (period - 1)) + dataframe['tr'][index]) / period

        return dataframe

    def ADX(self, dataframe):
        period = 14

        dataframe['dx'] = np.nan
        for index in range(0, dataframe.shape[0]):
            dataframe['dx'][index] = ((abs(dataframe['pdi'][index] - dataframe['ndi'][index])) / (abs(dataframe['pdi'][index] + dataframe['ndi'][index]))) * 100

        dataframe['adx'] = np.nan

        period2 = period*2
        dataframe['adx'][period2-1] = dataframe['dx'][period:period2].sum() / period
        for index in range(period2, dataframe.shape[0]):
            dataframe['adx'][index] = ((dataframe['adx'][index-1] * (period - 1)) + dataframe['dx'][index]) / period

        return dataframe


    def create_chart(self, dataframe):
        x = dataframe.index
        y = dataframe['adx']
        plt.plot(x, y)
        plt.show()

if __name__ == '__main__':
    hist = pandas.read_csv(r'savefunctiondata')
    hist = hist.set_index(pandas.to_datetime(hist['datetime']))
    hist.drop('datetime', axis=1, inplace=True)
    adx = Adx()
    data = adx.analyze(historical_data=hist)
    #data.to_csv('dmtest1', columns=['dx'], sep=' ')
    data.to_csv('dmtest1', columns= ['dx', 'adx'], sep=',')
    adx.create_chart(data)

