# Crypto Signals

Crypto Signals is automates your crpyto currency Technical Analysis (TA) and trading.

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
* Automtated buying/selling
* Bollinger Band
* Web Client :)


Shoutouts:
* To Bittrex for an awesome API
* Eric Somdahl for writing the Python wrapper for the Bittrex API
* Ryan Mullin for implementing the getHistoricalData() method on v2 of the Bittrex API

# How to use (Docker)
* First make sure you have [Docker installed](https://docs.docker.com/engine/installation/)
* Next, to create the docker image run `make build` in the root of the project directory.
* Once built copy template.env to .env and add your API keys, at a minimum read-only Bittrex keys are required.
* Make sure to also update the symbol\_pairs you'd like to monitor within app/default-config.json, following the symbol pair format in the second column found [here](https://gist.github.com/coinmining/95a21ad38f68f2da194052a8b066eca7)

## How to run
In the root directory run `docker-compose run app` or `make run` if you don't have docker-compose.

# How to use (Local)
To install the dependencies for this project, run "pip install -r requirements.txt" in the app directory.
You can add a secrets.json file to the app directory of your project to customize the configuration, the defaults are in app/default-config.json.

## How to run
Navigate to the app directory in your terminal and run with "python app.py"

# Liability
I am not your financial adviser, nor is this tool. Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any loses you may incur. Be wise and always do your own research.
