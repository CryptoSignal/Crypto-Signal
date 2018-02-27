# Crypto Signals

### Development state: Beta (Code is stable, documentation is often lagging)

### Join our community [Discord](https://discord.gg/MWTJVFf) channel!

Crypto Signals is a command line tool that automates your crypto currency Technical Analysis (TA).

Track over 500 coins across Bittrex, Bitfinex, GDAX, Gemini and more!

Technical Analysis Automated:
* Momentum
* Relative Strength Index (RSI)
* Ichimoku Cloud (Leading Span A, Leading Span B, Conversion Line, Base Line)
* Simple Moving Average
* Exponential Moving Average
* Breakouts / Pumps
* MACD

Alerts:
* SMS via Twilio
* Email
* Slack
* Telegram

Features:
* Modular code for easy trading strategy implementation
* Easy install with Docker

You can build on top of this tool and implement algorithm trading and some machine learning models to experiment with predictive analysis.

## Installing And Running
The commands listed below are intended to be run in a terminal.

1. Clone this repository. `git clone https://github.com/CryptoSignal/crypto-signal.git`

1. Create a settings.env file in the project directory.

1. Run application. `docker-compose pull && docker-compose run --rm app`

### Configuring settings.env

The environment variables you put into the settings.env file map to those found in [default-config.json](app/default-config.json). The way this works is that the name of the environment variables matches the path of the key in the JSON file.

For example lets say you wanted to scan only the markets ETH/BTC and DOGE/BTC, the default-config.json shows an empty array that will cause it to fetch all pairs:
```
{
  "settings": {
    "market_pairs": [],
...
```

To override this configration add the following line to settings.env `SETTINGS_MARKET_PAIRS=ETH/BTC,DOGE/BTC`.

Another common setting that users often want to override is which exchange to gather data from. Consider this from the default-config.json
```
...
  "exchanges": {
    "bittrex": {
      "required": {
        "enabled": true
      }
    }
  },
...
```
Lets turn off bittrex and turn on bitfinex, to do that we would add the following as two separate lines to settings.env: `EXCHANGES_BITTREX_REQUIRED_ENABLED=false` and `EXCHANGES_BITFINEX_REQUIRED_ENABLED=true`. You can find all available exchange id's [here](https://github.com/ccxt/ccxt/wiki/Exchange-Markets).

You can override any settings in the default-json.config file in the manner we have shown in the previous examples. When overriding Json arrays in settings.env they must be described as comma separated values without spaces.

# FAQ

## Common Questions

### Why does Tradingview show me different information than crypto-signal?
There are a number of reasons why the information crypto-signal provides could be different from tradingview and the truth is we have no way to be 100% certain of why the differences exist. Below are some things that affect the indicators that _may_ differ between crypto-signal and tradingview.

- tradingview will have more historical data and for some indicators this can make a [big difference](https://ta-lib.org/d_api/ta_setunstableperiod.html).

- tradingview uses a rolling 15 minute timeframe which means that the data they are analyzing can be more recent than ours by a factor of minutes or hours depending on what candlestick timeframe you are using.

- tradingview may collect data in a way that means the timeperiods we have may not line up with theres, which can have an effect on the analysis. This seems unlikely to us, but stranger things have happened.

### So if it doesn't match Tradingview how do you know your information is accurate?
Underpinning crypto-signal for most of our technical analysis is [TA-Lib](https://ta-lib.org/index.html) which is an open source technical analysis project started in 1999. This project has been used in a rather large number of technical analysis projects over the last two decades and is one of the most trusted open source libraries for analyzing candlestick data.

# Liability
I am not your financial adviser, nor is this tool. Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any loses you may incur. Be wise and always do your own research.
