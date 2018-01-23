# Crypto Signals

### Development state: Alpha (There are many bugs and documentation is often lagging)

Crypto Signals is a command line tool that automates your crypto currency Technical Analysis (TA) and trading.

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

Coming Soon:
* Automated buying/selling


# How to use (Docker)
* First make sure you have [Docker installed](https://docs.docker.com/engine/installation/)
* Next, to create the docker image run `make build` in the root of the project directory.
* Create a .env file which can be populated with settings in the format of OPTION=value which can be derived from the app/default-config.json file. For example if you want to change the how often it updates add SETTINGS\_UPDATE\_INTERVAL=600
* For lists of values separate them with commas. For instance if you want to use specific symbol pairs they are in the format of base\_currency/quote\_currency (i.e. SETTINGS\_MARKET\_PAIRS=BTC/ETH,BTC/USDT)

## How to run (Docker)
In the root directory run `docker-compose run app` or `make build && make run --env-file=.env` if you don't have docker-compose.

# How to use (Without Docker)
To install the dependencies for this project, perform the following...
- Ensure you are running python 3.6
- install TA-lib from https://www.ta-lib.org/ for your OS.
- `cd app`
- `pip install numpy==1.14.0`
- `pip install -r requirements.txt`

You can add a secrets.json file to the app directory of your project to customize the configuration, the defaults are in app/default-config.json.

## How to run (Without Docker)
Navigate to the app directory in your terminal and run with "python app.py"

# Behaviours

A behaviour is a functionality of the program that can be modified via the "selected\_task" value in `default-config.json`. It current accepts three values: 'default', 'rsi\_bot', 'reporter', and 'server'.

## Default

`"selected_task": "default"`

This is the default behaviour of the bot. By default, it polls Bittrex (or any other exchange you configured) and reports the price analysis of each coin pair available. This currently consists of six indicators: Breakout, RSI, SMA, EMA, Ichimoku Cloud, and MACD. More will be added in future versions.

## Simple Bot

`"selected_task": "simple_bot"`

This is still in development. Do not use it.

## Reporter

`"selected_task": "reporter"`

This is still in development. Do not use it.

## Server (Backtesting)

`"selected_task": "server"`

Forked from the Cryptocurrency Trading Bot Tutorial on: https://youtube.com/cryptocurrencytrading

This behaviour runs a flask server hosting a website allowing you to test different backtesting strategies on various sets of historical data.

![Alt text](/backtesting-ui.png "Backtesting UI")

### Installation

First, clone or download the repository to your computer.

**Front End**- Navigate to the *app/behaviours/ui/www* directory and run `npm install`. Make sure you have the latest version of node.js installed on your computer.

**Back End**- (Without Docker) The server should run with python 3.x. Assuming you have already installed all the dependencies, you're in the clear.

(With Docker) Everything should be installed already from the dependencies if you run `make build` in the root directory of crypto-signal.


### Running the Application

First, you'll need to use webpack to bundle all of the React .jsx files on the front end. Navigate to the *app/beahviours/ui/www* directory and run `npm run build`.

If you haven't already, **ensure you have changed the "selected_task" value from "default" to "server" in default-config.json.**

(Without Docker) Navigate to the *app/* directory and run `python app.py`.

(With Docker) Run `docker-compose up` in the root directory.

Now you're all set! Open up your favorite browser and navigate to http://localhost:5000/ and try it out.

### How does it work?

First, you'll select the exchange and coin pair you want to test your strategy over.

"Capital" is the amount of BTC you want to start out with trading.

"Time Unit" is the duration of each point on the time series of historical data (1m, 5m, 30m, etc.).

"Stop Loss" is the percentage below each buy price that you will sell your position at. The smaller the stop loss, the less your risk. A value of 0 means no stop loss, i.e. you sell if and only if your sell conditions are true.

"Start Time" is the start date that your backtesting data will be grabbed from.

### Strategies

The middle panel on the website allows you to create customizable strategies to run over your historical data. You can choose from various indicators and select a comparision operator to compare the indicator on the left to another indicator or a number. The "value" field on the right can take either numbers (i.e. "30", "0.00034") or one of the suggested indicators from the dropdown (i.e. "RSI", "Current Price"). Any other inputs are invalid. This will be improved on in the future for better user experience.

There are two buttons below the buy and sell strategy fields. Clicking on the "+" button will add another condition to your strategy. Clicking on the "-" button will remove the most recently added condition. You may add as many of these as you want. As of right now, if multiply strategy conditions are present they will be evaluated conjunctively. In other words, if your "Buy When" conditions are

```
RSI < 40
Current Price < Moving Average (15 Period)
```

Then the bot will buy only when **both conditions are true**. The same applies for the sell conditions.

### What's on the Graph?

Green dots represent buy points. Red dots represent sell points. The blue line is the plot of historical closing prices, and the dotted yellow lines are Bollinger Bands. Moving averages will appear red and green, but this will be customizable later.

### Coming Soon

MACD plot, RSI plot

# Liability
I am not your financial adviser, nor is this tool. Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any loses you may incur. Be wise and always do your own research.
