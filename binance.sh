#!/usr/bin/bash

cat /dev/null > cur.txt
curl https://coinmarketcap.com/exchanges/binance/  | grep -o '_BTC[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/binance/  | grep -o '_USDT[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/binance/  | grep -o '_ETH[^<]*' | grep -o '[^>]*$' >> cur.txt
sed 's/^/    - /' cur.txt > coins
