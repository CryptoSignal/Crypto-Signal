# CryptoSignal - #1 Quant Trading & Technical Analysis Bot - 4,100+ stars & 1,000+ forks https://github.com/CryptoSignal/Crypto-Signal

### Development state: Beta (Code is stable, documentation is often lagging)

### Join our community [Discord](https://discord.gg/MWTJVFf) channel! (2,100+ members)

Crypto Signals is a command line tool that automates your crypto currency Technical Analysis (TA). It is maintained by a community of traders, engineers, data scientists, PMs, & countless generous individuals who wish to democratize the equal & open access to the greatest wealth re-distribution experiment in human and monetary policy history - Bitcoin

## Track over 500 coins across Bittrex, Binance, Bittrex, Bitfinex, Coinbase, Gemini and more!
(Subject to local financial regulations under the jurisdiction you and your financial activities are under. Marketing or enabling does not imply nor justify the facilitation or condoning of any activity - financial or otherwise. You assume and bare all risk. Be careful & act wisely.)

## Technical Analysis Automated:
* Momentum
* Relative Strength Index (RSI)
* Ichimoku Cloud (Leading Span A, Leading Span B, Conversion Line, Base Line)
* Simple Moving Average
* Exponential Moving Average
* MACD
* MFI
* OBV
* VWAP

## Alerts:
* SMS via Twilio
* Email
* Slack
* Telegram
* Discord

## Features:
* Modular code for easy trading strategy implementation
* Easy install with Docker

You can build on top of this tool and implement algorithm trading and some machine learning models to experiment with predictive analysis.

### Founded by Abenezer Mamo @ www.Mamo.io & www.linkedin.com/in/AbenezerMamo

## Installing And Running
The commands listed below are intended to be run in a terminal.

1. Install [docker CE](https://docs.docker.com/install/)

1. Create a config.yml file in your current directory. See the Configuring config.yml section below for customizing settings.

1. In a terminal run the application. `docker run --rm -v $PWD/config.yml:/app/config.yml shadowreaver/crypto-signal:master`.

1. When you want to update the application run `docker pull shadowreaver/crypto-signal:master`

### Configuring config.yml

For a list of all possible options for config.yml and some example configurations look [here](docs/config.md)

# FAQ

## Common Questions

### Why does Tradingview show me different information than crypto-signal?
There are a number of reasons why the information crypto-signal provides could be different from tradingview and the truth is we have no way to be 100% certain of why the differences exist. Below are some things that affect the indicators that _may_ differ between crypto-signal and tradingview.

- tradingview will have more historical data and for some indicators this can make a [big difference](https://ta-lib.org/d_api/ta_setunstableperiod.html).

- tradingview uses a rolling 15 minute timeframe which means that the data they are analyzing can be more recent than ours by a factor of minutes or hours depending on what candlestick timeframe you are using.

- tradingview may collect data in a way that means the timeperiods we have may not line up with theirs, which can have an effect on the analysis. This seems unlikely to us, but stranger things have happened.

### So if it doesn't match Tradingview how do you know your information is accurate?
Underpinning crypto-signal for most of our technical analysis is [TA-Lib](https://ta-lib.org/index.html) which is an open source technical analysis project started in 1999. This project has been used in a rather large number of technical analysis projects over the last two decades and is one of the most trusted open source libraries for analyzing candlestick data.

# Liability
I am not your financial adviser, nor is this tool. Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any losses you may incur. Be wise and always do your own research.

We recommend you begin by learning the core principles used in traditional asset classes since they are less volatile & apply your knowledge in simulated trading before liquidating your dreams.
