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


def calculateSMA(coin_pair, period, unit):
    historical_data = my_bittrex.getHistoricalData(coin_pair, period, unit)
    total_closing = []
    for i in historical_data:
        total_closing.append(i['C'])
    return (sum(total_closing) / period)

def calculateEMA(coin_pair, period, unit):
    historical_data = my_bittrex.getHistoricalData(coin_pair, period, unit)
    return historical_data

def calculateRSI(coin_pair, period, unit):
    historical_data = my_bittrex.getHistoricalData(coin_pair, period, unit)
    return historical_data

def findBreakout(coin_pair, period, unit):
    historical_data = my_bittrex.getHistoricalData(coin_pair, period, unit)



print(calculateSMA(coin_pair='BTC-ETH', period=30, unit="thirtyMin"))
