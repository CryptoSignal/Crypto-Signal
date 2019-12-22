#!/usr/bin/bash

cat /dev/null > cur.txt
curl https://coinmarketcap.com/exchanges/bitfinex/ | grep -o ':BTC[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/bitfinex/ | grep -o ':USDT[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/bitfinex/ | grep -o ':USD[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/bitfinex/ | grep -o ':ETH[^<]*' | grep -o '[^>]*$' >> cur.txt
sed 's/^/    - /' cur.txt > coins
