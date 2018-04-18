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
* MFI
* VWAP

Alerts:
* SMS via Twilio
* Email
* Slack
* Telegram
* Discord

Features:
* Modular code for easy trading strategy implementation
* Easy install with Docker

You can build on top of this tool and implement algorithm trading and some machine learning models to experiment with predictive analysis.

## Installing And Running
The commands listed below are intended to be run in a terminal.

1. Install [docker CE](https://docs.docker.com/install/)

1. Create a settings.env file in your current directory. See the Configuring settings.env section below for customizing settings.

1. In a terminal run the application. `docker run --rm --env-file=settings.env shadowreaver/crypto-signal:master`.

1. When you want to update the application run `docker pull shadowreaver/crypto-signal:master`

### Configuring settings.env

For a list of all possible options for settings.env and some example configurations look [here](docs/config.md)

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
Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any losses you may incur. Be wise and always do your own research.
