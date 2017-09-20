from bittrex import Bittrex
import json
import time
import os
from twilio.rest import Client

# Creating an instance of the Bittrex class with our secrets.json file
with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()
    my_bittrex = Bittrex(secrets['bittrex_key'], secrets['bittrex_secret'])

# Setting up Twilio for SMS alerts
account_sid = secrets['twilio_key']
auth_token = secrets['twilio_secret']
client = Client(account_sid, auth_token)


# Let's test an API call to get our BTC balance as a test
# print(my_bittrex.get_balance('BTC')['result']['Balance'])

coin_pairs = ['BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-CVC', 'BTC-BAT', 'BTC-XEL', 'BTC-STRAT', 'BTC-LSK', 'BTC-BCC', 'BTC-NEO', 'BTC-OK', 'BTC-TRIG', 'BTC-PAY', 'BTC-XMR']

#print(historical_data = my_bittrex.getHistoricalData('BTC-ETH', 30, "thirtyMin"))
def getClosingPrices(coin_pair, period, unit):
    """
    Returns closing prices within a specified time frame for a coin pair
    :type coin_pair: str
    :type period: str
    :type unit: int
    :return: Array of closing prices
    """
    historical_data = my_bittrex.getHistoricalData(coin_pair, period, unit)
    closing_prices = []
    for i in historical_data:
        closing_prices.append(i['C'])
    return closing_prices

def calculateSMA(coin_pair, period, unit):
    """
    Returns the Simple Moving Average for a coin pair
    """

    total_closing = sum(getClosingPrices(coin_pair, period, unit))
    return (total_closing / period)

def calculateEMA(coin_pair, period, unit):
    """
    Returns the Exponential Moving Average for a coin pair
    """

    closing_prices = getClosingPrices(coin_pair, period, unit)
    previous_EMA = calculateSMA(coin_pair, period, unit)
    constant = (2 / (period + 1))
    current_EMA = (closing_prices[-1] * (2 / (1 + period))) + (previous_EMA * (1 - (2 / (1 + period))))
    return current_EMA

def calculateRSI(coin_pair, period, unit):
    """
    Calculates the Relative Strength Index for a coin_pair
    """
    closing_prices = getClosingPrices(coin_pair, period, unit)

def findBreakout(coin_pair, period, unit):
    """
    Finds breakout based on how close the High was to Closing and Low to Opening
    """
    hit = 0
    historical_data = my_bittrex.getHistoricalData(coin_pair, period, unit)
    for i in historical_data:
        if (i['C'] == i['H']) and (i['O'] == i['L']):
            hit += 1

    if (hit / period) >= .75:
        message = client.api.account.messages.create(to=secrets['my_number'],from_=secrets['twilio_number'],body="{} is breaking out!".format(coin_pair))
        return "{}: BREAKING OUT!!!".format(coin_pair)
    else:
        return "{}: #Bagholding".format(coin_pair)


if __name__ == "__main__":
    def loop_script():
        for i in coin_pairs:
            print(findBreakout(coin_pair=i, period=5, unit="fiveMin"))
        time.sleep(60)
        loop_script()
    loop_script()
