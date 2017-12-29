# Crypto Signals

Track 250+ crypto currencies and their trading signals through Crypto signals.

Technical Analysis Automated:
* Relative Strength Index (RSI)
* Ichimoku Cloud (Leading Span A, Leading Span B, Conversion Line, Base Line)
* Simple Moving Average
* Exponential Moving Average
* Breakouts

Features:
* Tracking for over 250 coins on Bittrex
* SMS alerts for coin breakouts and price changes
* Well documented script
* Automated Technical Analysis that's implemented from scratch for simplicity and ease of use

You can build on top of this tool and implement algorithm trading and some machine learning models to experiment with predictive analysis.

Coming Soon:
* MACD
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
* Make sure to also update the market\_pairs environment or app.py variable with comma seperated market pair values that match Bittrex's format (i.e. BTC-ETH)

## How to run
In the root directory run `docker-compose run app` or `make run` if you don't have docker-compose.

# How to use (Local)
To install the dependencies for this project, run "pip install -r requirements.txt" in the app directory.
Add a secrets.json file to the app directory of your project.
The contents of the file should mirror the following:

```json
{
    "bittrex_key" : "BITTREX_API_KEY",
    "bittrex_secret" : "BITTREX_SECRET",
    "twilio_key": "TWILIO_API_KEY",
    "twilio_secret": "TWILIO_SECRET",
    "twilio_number": "TWILIO_PHONE_NUMBER",
    "my_number": "YOUR_PHONE_NUMBER",
    "gmail_username": "GMAIL_USERNAME",
    "gmail_password": "GMAIL_PASSWORD",
    "gmail_address_list": [
        "EXAMPLE_RECIPIENT_1@GMAIL.COM",
        "EXAMPLE_RECIPIENT_2@GMAIL.COM",
        "ETC..."
    ]
}
```

If you don't want to use the Twilio or Gmail notifications, leave them as the default values.

## How to run
Navigate to the app directory in your terminal and run with "python app.py"

# Liability
I am not your financial adviser, nor is this tool. Use this program as an educational tool, and nothing more. None of the contributors to this project are liable for any loses you may incur. Be wise and always do your own research.
