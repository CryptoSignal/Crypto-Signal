#!/usr/bin/bash

cat /dev/null > cur.txt
curl https://coinmarketcap.com/exchanges/okex/ | grep -o '_btc[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/okex/ | grep -o '_usdt[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/okex/ | grep -o '_usd[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/okex/ | grep -o '_eth[^<]*' | grep -o '[^>]*$' >> cur.txt
sed 's/^/    - /' cur.txt > coins
