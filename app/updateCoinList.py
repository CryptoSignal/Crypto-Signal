import yaml
import subprocess
from subprocess import call
import sys

output = call(["sh",sys.argv[1]])

coinStream = open("coins","r")
newList=[]
for coin in coinStream:
    if coin.find('/') >= 0:
        newList.append(coin.split('-')[1].strip())    
stream = open(sys.argv[2], "r")
data = yaml.safe_load(stream)
data['settings']['market_pairs'] = newList

with open(sys.argv[2], 'w') as f:
    yaml.dump(data, f)
