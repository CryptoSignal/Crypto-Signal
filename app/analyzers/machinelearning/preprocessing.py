import pandas as pd
from sklearn import preprocessing
import seaborn as sb
import matplotlib.pyplot as plt

class Preprocessing():
    def Cleansing(self, historical_data, target_name):
        """Preprocessing data for machinelearning usage

        Args:
            historical_data (list): A matrix of historical data.
            target_name (string): The target variable name.

        Returns:
            pandas.DataFrame: Two dataframe, one containing features, the other target variable.
        """
        y = historical_data[target_name].copy()
        del historical_data[target_name]
        x = historical_data.copy()
        x.dropna(how='all', inplace=True)
        x_scaled = pd.DataFrame(preprocessing.scale(x))
        return x_scaled, y

    def correlation_matrix(self, data_set):
        """Show correlation matrix plot

        Args:
            data_set (pandas.DataFrame): A dataframe of data.

        Returns:
            pandas.DataFrame: A dataframe contains correlation matrix.
        """
        data_set_corr = data_set.corr()
        sb.set(rc={'figure.figsize': (20, 20)})
        sb.heatmap(data_set_corr, cmap="Blues", center=0, annot=True)
        plt.show()
        return data_set_corr