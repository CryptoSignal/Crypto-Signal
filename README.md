# Crypto Signals

Crypto Signals is a command line tool that automates your crypto currency Technical Analysis (TA).

It is based on [Crypto Signals] https://github.com/CryptoSignal/crypto-signal , so I recommend you to take a look in that proyect to known what is it.

I'm making minor changes and adding some features in this repo because the original CryptoSignal project is no longer maintained.

## Changes
- It creates candle bar charts with MAs, RSI and MACD. These images can be sent as part of a Telegram notification.
- It allows to include prices as part of the notification message.

## Installing And Running
The commands listed below are intended to be run in a terminal.

1. Clone this repo

1. Create a config.yml file and put it into "app" folder.

1. Build your own Docker image, for example `docker build -t laliux/crypto-signals:latest .`

1. For testing and debugging run `docker run --rm -ti -v  $PWD/app:/app laliux/crypto-signals:latest`

1. For production run in daemon mode `docker run --rm -di -v  $PWD/app:/app laliux/crypto-signals:latest`


### Configuring config.yml

All possible options for config.yml are almost the same for original CryptoSignal, so look [here](docs/config.md)

At the moment the only aditional option is to enable/disable charts creation.

```
settings:
    log_level: INFO
    update_interval: 600
    enable_charts: true
    market_pairs:
        - XRP/USDT
        - ETH/USDT
        - BTC/USDT
        ....
```

Finally, if you want prices, you can configure your messages template.

```
notifiers:
    telegram:
        required:
            token: 791615820:AAGFgGSumWUrb-CyXtGxzAuYaabababababababa
            chat_id: 687950000
        optional:
            parse_mode: html
            template: "[{{analysis.config.candle_period}}] {{market}} {{values}} Prices: [{{prices}}]"
```


# Liability
I am not your financial adviser, nor is this tool. Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any losses you may incur. Be wise and always do your own research.
