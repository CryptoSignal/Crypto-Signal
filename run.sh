kill -9 `ps -ef | grep app.py | awk '{print $2}'`
cat /dev/null > result_h.log
cat /dev/null > result_d.log
cat /dev/null > result_w.log

python3 app/updateCoinList.py bittrex.sh bittrex.yml
sleep 5
python3 app/updateCoinList.py bitfinex.sh bitfinex.yml
sleep 5
python3 app/updateCoinList.py bitfinex.sh bitfinex_d.yml
sleep 5
python3 app/updateCoinList.py bitfinex.sh bitfinex_w.yml
sleep 5
python3 app/updateCoinList.py binance.sh binance.yml
sleep 5
python3 app/updateCoinList.py binance.sh binance_d.yml
sleep 5
python3 app/updateCoinList.py binance.sh binance_w.yml
sleep 5
python3 app/updateCoinList.py huobi.sh huobi.yml
sleep 5
python3 app/updateCoinList.py huobi.sh huobi_d.yml
sleep 5
python3 app/updateCoinList.py huobi.sh huobi_w.yml

python3 app/app.py  bittrex.yml result_d.log &
#python3 app/app.py  bittrex_w.yml result_w.log &

python3 app/app.py  bitfinex.yml result_h.log &
python3 app/app.py  bitfinex_d.yml  result_d.log &
python3 app/app.py  bitfinex_w.yml result_w.log &

python3 app/app.py  binance.yml result_h.log &
python3 app/app.py  binance_d.yml result_d.log &
python3 app/app.py  binance_w.yml result_w.log &

python3 app/app.py  huobi.yml result_h.log &
python3 app/app.py  huobi_d.yml result_d.log &
python3 app/app.py  huobi_w.yml result_w.log &
