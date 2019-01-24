from __builtin__ import file
from CodeWarrior.Standard_Suite import line


def main():
    matchCoinPairsToUsdt("cur.txt");
    
    
def matchCoinPairsToUsdt(curFile):
    usdtMap={}
    btcEthMap={}
    raw = open(curFile, 'r+')
    with raw as f:
        for line in f:
            coin = line.strip().split("/")
            if coin[1] == 'USDT':
                usdtMap[coin[0]] = 1;
            else:
                btcEthMap[coin[0]] = 1;
  
    for entry in btcEthMap:
        if(entry not in usdtMap):
            usdtMap[entry] = 1;
         
    write = open(curFile, "w")
    with write as f:
        for entry in usdtMap:
            f.write(entry+"/USDT"+"\n")

    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    
    