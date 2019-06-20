kill -9 `ps -ef | grep app.py | awk '{print $1}'`

#update username locally
#find custom/*.yml -type f -exec sed -i '' -e "s/lfz.carlos/cryptalsender/" {} \;
#find easy/*.yml -type f -exec sed -i '' -e "s/lfz.carlos/cryptalsender/" {} \;

#update emails run locally
#python3 app/updateCoinList.py binance.sh easy/binance_1h_easy.yml 
#rm -rf *easyFileName

export modes=(easy custom)
cat /dev/null > h${modes[i]}.log
cat /dev/null > d${modes[i]}.log
cat /dev/null > w${modes[i]}.log

for(( i=0;i<${#modes[@]};i++)); do

    python3 app/updateCoinList.py bittrex.sh ${modes[i]}/bittrex_1h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py bittrex.sh ${modes[i]}/bittrex_1d_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py bitfinex.sh ${modes[i]}/bitfinex_1h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py bitfinex.sh ${modes[i]}/bitfinex_6h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py bitfinex.sh ${modes[i]}/bitfinex_d_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py bitfinex.sh ${modes[i]}/bitfinex_w_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py binance.sh ${modes[i]}/binance_1h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py binance.sh ${modes[i]}/binance_4h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py binance.sh ${modes[i]}/binance_d_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py binance.sh ${modes[i]}/binance_w_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py huobi.sh ${modes[i]}/huobi_1h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py huobi.sh ${modes[i]}/huobi_d_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py huobi.sh ${modes[i]}/huobi_w_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py okex.sh ${modes[i]}/okex_1h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py okex.sh ${modes[i]}/okex_4h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py okex.sh ${modes[i]}/okex_6h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py okex.sh ${modes[i]}/okex_d_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py okex.sh ${modes[i]}/okex_w_${modes[i]}.yml
    sleep 10

    python3 app/updateCoinList.py zb.sh ${modes[i]}/zb_1h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py zb.sh ${modes[i]}/zb_4h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py zb.sh ${modes[i]}/zb_6h_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py zb.sh ${modes[i]}/zb_d_${modes[i]}.yml
    sleep 10
    python3 app/updateCoinList.py zb.sh ${modes[i]}/zb_w_${modes[i]}.yml
    sleep 10
done


for(( i=0;i<${#modes[@]};i++)); do
    #python3 app/app.py  ${modes[i]}/bittrex_1h_${modes[i]}.yml ${modes[i]}/bittrex_1h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/bittrex_1d_${modes[i]}.yml ${modes[i]}/bittrex_1d.log ${modes[i]} &

    #python3 app/app.py  ${modes[i]}/bitfinex_1h_${modes[i]}.yml ${modes[i]}/bitfinex_1h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/bitfinex_6h_${modes[i]}.yml ${modes[i]}/bitfinex_6h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/bitfinex_d_${modes[i]}.yml  ${modes[i]}/bitfinex_d.log ${modes[i]} &
    if [ ${modes[i]} = 'custom' ]
    then
        python3 app/app.py  ${modes[i]}/bitfinex_w_${modes[i]}.yml ${modes[i]}/bitfinex_w.log ${modes[i]} &
    fi

    python3 app/app.py  ${modes[i]}/binance_1h_${modes[i]}.yml ${modes[i]}/binance_1h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/binance_4h_${modes[i]}.yml ${modes[i]}/binance_4h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/binance_d_${modes[i]}.yml ${modes[i]}/binance_d.log ${modes[i]} &
    if [ ${modes[i]} = 'custom' ]
    then
        python3 app/app.py  ${modes[i]}/binance_w_${modes[i]}.yml ${modes[i]}/binance_w.log ${modes[i]} &
    fi

    python3 app/app.py  ${modes[i]}/huobi_1h_${modes[i]}.yml ${modes[i]}/huobi_1h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/huobi_d_${modes[i]}.yml ${modes[i]}/huobi_d.log ${modes[i]} &
    if [ ${modes[i]} = 'custom' ]
    then
        python3 app/app.py  ${modes[i]}/huobi_w_${modes[i]}.yml ${modes[i]}/huobi_w.log ${modes[i]} &
    fi

    python3 app/app.py  ${modes[i]}/okex_1h_${modes[i]}.yml ${modes[i]}/okex_1h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/okex_4h_${modes[i]}.yml ${modes[i]}/okex_4h.log ${modes[i]} &
#    python3 app/app.py  ${modes[i]}/okex_6h_${modes[i]}.yml ${modes[i]}/okex_6h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/okex_d_${modes[i]}.yml ${modes[i]}/okex_d.log ${modes[i]} &
    if [ ${modes[i]} = 'custom' ]
    then
       python3 app/app.py  ${modes[i]}/okex_w_${modes[i]}.yml ${modes[i]}/okex_w.log ${modes[i]} &
    fi

    python3 app/app.py  ${modes[i]}/zb_1h_${modes[i]}.yml ${modes[i]}/zb_1h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/zb_4h_${modes[i]}.yml ${modes[i]}/zb_4h.log ${modes[i]} &
#   python3 app/app.py  ${modes[i]}/zb_6h_${modes[i]}.yml ${modes[i]}/zb_6h.log ${modes[i]} &
    python3 app/app.py  ${modes[i]}/zb_d_${modes[i]}.yml ${modes[i]}/zb_d.log ${modes[i]} &
    if [ ${modes[i]} = 'custom' ]
    then
       python3 app/app.py  ${modes[i]}/zb_w_${modes[i]}.yml ${modes[i]}/zb_w.log ${modes[i]} &
    fi

done
