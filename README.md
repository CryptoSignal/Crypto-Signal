# Crypto Signals

### Development state: Alpha (There are many bugs and documentation is often lagging)

### Join our community [Discord](https://discordapp.com/invite/hXdCgCE) channel!

Crypto Signals is a command line tool that automates your crypto currency Technical Analysis (TA).

Track over 500 coins across Bittrex, Bitfinex, GDAX, Gemini and more!

Technical Analysis Automated:
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

# How to use
* First make sure you have [Docker installed](https://docs.docker.com/engine/installation/)
* Next, to create the docker image run `make build` in the root of the project directory.
* Create a settings.env file which can be populated with settings in the format of OPTION=value which can be derived from the app/default-config.json file. For example if you want to change the how often it updates add SETTINGS\_UPDATE\_INTERVAL=600
* For lists of values separate them with commas. For instance if you want to use specific symbol pairs they are in the format of base\_currency/quote\_currency (i.e. SETTINGS\_MARKET\_PAIRS=BTC/ETH,BTC/USDT)

## How to run
In the root directory run `docker-compose run app` or `make build && make run --env-file=settings.env` if you don't have docker-compose.

By default, it polls Bittrex (or any other exchange you configured) and reports the price analysis of each coin pair available. This currently consists of six indicators: Breakout, RSI, SMA, EMA, Ichimoku Cloud, and MACD. More will be added in future versions.

# Liability
I am not your financial adviser, nor is this tool. Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any loses you may incur. Be wise and always do your own research.
