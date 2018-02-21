# Crypto Signals

### Development state: Beta (Code is stable documentation is often lagging)

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

## How to use
* First make sure you have [Docker installed](https://docs.docker.com/engine/installation/)
* Next, to create the docker image run `make build` in the root of the project directory.
* Create a settings.env file which can be populated with settings in the format of OPTION=value which can be derived from the app/default-config.json file. For example if you want to change the how often it updates add SETTINGS\_UPDATE\_INTERVAL=600
* For lists of values separate them with commas. For instance if you want to use specific symbol pairs they are in the format of base\_currency/quote\_currency (i.e. SETTINGS\_MARKET\_PAIRS=BTC/ETH,BTC/USDT)

## How to run
In the root directory run `docker-compose run app` or `make build && make run --env-file=settings.env` if you don't have docker-compose.

By default, it polls Bittrex (or any other exchange you configured) and reports the price analysis of each coin pair available. This currently consists of six indicators: Breakout, RSI, SMA, EMA, Ichimoku Cloud, and MACD. More will be added in future versions.

# FAQ

## Installing And Running
The commands listed below are intended to be run in a terminal.

### Linux & OSX
0. Clone this repository. `git clone https://github.com/AbenezerMamo/crypto-signal.git`

0. Build the docker image. `make build`

0. Create a settings.env file in the project directory. `touch settings.env`

0. Add the settings you want to settings.env, see Common Settings below.

0. Run application. `docker-compose run --rm app`

### Windows
0. Clone this repository. `git clone https://github.com/AbenezerMamo/crypto-signal.git`

0. Build the docker image. `docker build -t crypto-signal:latest .`

0. Create a settings.env file in the project directory. Create it with windows explorer or your favourite editor.

0. Add the settings you want to settings.env, see Common Settings below.

0. Run application. `docker-compose run --rm app`

### Common Settings
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
Lets turn off bittrex and turn on bitfinex, to do that we would add the following two lines to settings.env: `EXCHANGES_BITTREX_REQUIRED_ENABLED=false` and `EXCHANGES_BITFINEX_REQUIRED_ENABLED=true`. You can find all available exchange id's [here](https://github.com/ccxt/ccxt/wiki/Exchange-Markets).

You can override any settings in the default-json.config file in the manner we have shown in the previous examples. When overriding Json arrays in settings.env they must be described as comma separated values without spaces.

## Common Questions

### Why does Tradingview show me different information than crypto-signal?
There are a number of reasons why the information crypto-signal provides could be different from tradingview and the truth is we have no way to be 100% certain of why the differences exist. Below are some things that affect the indicators that _may_ differ between crypto-signal and tradingview.

- tradingview will have more historical data and for some indicators this can make a [big difference](https://ta-lib.org/d_api/ta_setunstableperiod.html).

- tradingview may collect data in a way that means the timeperiods we have may not line up with theres, which can have an effect on the analysis.

- tradingview may use a rolling timeframe which means that the data they may be analyzing is several hours ahead of what we are analyzing.

We know that dot point 1 is definitely a factor, the other two factors are just hypothesis at this point.

### So if it doesn't match Tradingview how do you know your information is accurate?
Underpinning crypto-signal for most of our technical analysis is [TA-Lib](https://ta-lib.org/index.html) which is an open source technical analysis project started in 1999. This project has been used in a rather large number of technical analysis projects over the last two decades and is one of the most trusted open sources for analyzing candlestick data.


# Liability
I am not your financial adviser, nor is this tool. Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any loses you may incur. Be wise and always do your own research.
