#!/usr/bin/bash

cat /dev/null > cur.txt
curl https://coinmarketcap.com/exchanges/zb-com/ | grep -o 'btc[^<]*' | grep -o '[^>]*$' >> cur.txt
curl https://coinmarketcap.com/exchanges/zb-com/ | grep -o 'usdt[^<]*' | grep -o '[^>]*$' >> cur.txt
sed 's/^/    - /' cur.txt > coins
