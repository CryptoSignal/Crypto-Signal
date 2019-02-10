kill -9 `ps -ef | grep app.py | awk '{print $1}'`
cat /dev/null > result_h.log
cat /dev/null > result_d.log
cat /dev/null > result_w.log

python3 app/updateCoinList.py bittrex.sh bittrex_1h.yml
sleep 5
python3 app/updateCoinList.py bittrex.sh bittrex_1d.yml
sleep 5
python3 app/updateCoinList.py bitfinex.sh bitfinex_1h.yml
sleep 5
python3 app/updateCoinList.py bitfinex.sh bitfinex_6h.yml
sleep 5
python3 app/updateCoinList.py bitfinex.sh bitfinex_d.yml
sleep 5
python3 app/updateCoinList.py bitfinex.sh bitfinex_w.yml
sleep 5
python3 app/updateCoinList.py binance.sh binance_1h.yml
sleep 5
python3 app/updateCoinList.py binance.sh binance_4h.yml
sleep 5
python3 app/updateCoinList.py binance.sh binance_d.yml
sleep 5
python3 app/updateCoinList.py binance.sh binance_w.yml
sleep 5
python3 app/updateCoinList.py huobi.sh huobi_1h.yml
sleep 5
python3 app/updateCoinList.py huobi.sh huobi_d.yml
sleep 5
python3 app/updateCoinList.py huobi.sh huobi_w.yml
sleep 5

python3 app/app.py  bittrex_1h.yml result_bittrex_1h.log &
python3 app/app.py  bittrex_1d.yml result_bittrex_1d.log &

python3 app/app.py  bitfinex_1h.yml result_bitfinex_1h.log &
python3 app/app.py  bitfinex_6h.yml result_bitfinex_6h.log &
python3 app/app.py  bitfinex_d.yml  result_bitfinex_d.log &
python3 app/app.py  bitfinex_w.yml result_bitfinex_w.log &

python3 app/app.py  binance_1h.yml result_binance_1h.log &
python3 app/app.py  binance_4h.yml result_binance_4h.log &
python3 app/app.py  binance_d.yml result_binance_d.log &
python3 app/app.py  binance_w.yml result_binance_w.log &

python3 app/app.py  huobi_1h.yml result_huobi_1h.log &
python3 app/app.py  huobi_d.yml result_huobi_d.log &
python3 app/app.py  huobi_w.yml result_huobi_w.log &
