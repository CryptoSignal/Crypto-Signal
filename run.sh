kill -9 `ps -ef | grep app.py | awk '{print $2}'`
cat /dev/null > result_h.log
cat /dev/null > result_d.log
cat /dev/null > result_w.log

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
