sh mxc.sh > coins
sed -i '' 's/\/USDT//g' "coins"
sed -i '' 's/\/ETH//g' "coins"
sed -i '' 's/\/BTC//g' "coins"
sed -i '' 's/    - //g' "coins"
curl get https://coinmarketcap.com/coins/views/all/ > coins.all
python coinVolumeCheck.py
