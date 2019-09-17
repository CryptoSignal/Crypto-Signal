from bs4 import BeautifulSoup

text = open("coins.all")
coins = open("coins","r")
volumeDict = {}

#pre-load publish volume map
doc = BeautifulSoup(text)
trs = doc.findAll('tr')
for tr in trs:
        if( tr.find('td')):
            td_name = tr.findAll('td')[2]
            td_supply = tr.findAll('td')[5]
            volumeDict[td_name.text.strip()] = td_supply['data-sort']  


condition = lambda supply : supply < 1100000000.1

#scan coin by conditions
result = {}
for coin in coins:
    coin = coin.strip()
    if coin in volumeDict and condition(float(volumeDict[coin])):
        result[coin] = volumeDict[coin]

for item in result:        
    print('{0}:{1}'.format(item, result[item]))

