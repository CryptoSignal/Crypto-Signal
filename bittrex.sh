#!/usr/bin/bash

cat /dev/null > cur.txt
curl https://coinmarketcap.com/exchanges/bittrex/ | grep -o 'BTC-[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/bittrex/ | grep -o 'ETH-[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/bittrex/ | grep -o 'USDT-[^<]*' | grep -o '[^>]*$' >> cur.txt
sed 's/^/    - /' cur.txt > coins
