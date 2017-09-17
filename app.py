from bittrex import Bittrex
import json

with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()
    my_bittrex = Bittrex(secrets['key'], secrets['secret'])

# Let's test an API call to get our BTC balance as a test
# print(my_bittrex.get_balance('BTC')['result']['Balance'])

coin_pairs = ['BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-CVC']


#print(historical_data = my_bittrex.getHistoricalData('BTC-ETH', 30, "thirtyMin"))
def getClosingPrices(coin_pair, period, unit):
    historical_data = my_bittrex.getHistoricalData(coin_pair, period, unit)
    closing_prices = []
    for i in historical_data:
        closing_prices.append(i['C'])
    return closing_prices

def calculateSMA(coin_pair, period, unit):
    total_closing = sum(getClosingPrices(coin_pair, period, unit))
    return (total_closing / period)

def calculateEMA(coin_pair, period, unit):
    closing_prices = getClosingPrices(coin_pair, period, unit)
    previous_EMA = calculateSMA(coin_pair, period, unit)
    constant = (2 / (period + 1))
    current_EMA = (closing_prices[-1] * (2 / (1 + period))) + (previous_EMA * (1 - (2 / (1 + period))))
    return current_EMA

def calculateRSI(coin_pair, period, unit):
    closing_prices = getClosingPrices(coin_pair, period, unit)

def findBreakout(coin_pair, period, unit):
    closing_prices = getClosingPrices(coin_pair, period, unit)



print(calculateEMA(coin_pair='BTC-ETH', period=10, unit="thirtyMin"))
