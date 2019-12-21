import sys

def main():
    matchCoinPairsToUsdt(sys.argv[1]);
    
    
def matchCoinPairsToUsdt(curFile):
    usdtMap={}
    btcEthMap={}
    raw = open(curFile, 'r+')
    with raw as f:
        for line in f:
            coinPair = line.strip().split(" ")
            coin = coinPair[1].strip().split("/")
            if coin[1] == 'USDT' or coin[1] == 'USD':
                usdtMap[coin[0]] = 1;
            else:
                btcEthMap[coin[0]] = 1;
  
    for entry in btcEthMap:
        if(entry not in usdtMap):
            usdtMap[entry] = 1;
         
    write = open(curFile, "w")
    with write as f:
        for entry in usdtMap:
            f.write(entry+"USD"+"\n")

    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    
    
