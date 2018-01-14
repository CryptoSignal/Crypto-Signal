# Cryptocurrency Trading Bot

Taken from the Cryptocurrency Trading Bot Tutorial on: https://youtube.com/cryptocurrencytrading

I have made significant improvements in adding new indicators and integrated the backtesting bot with a UI.

![Alt text](/cryptobot.jpg "The dashboard")

This tool allows you to try different strategies over sets of historical trading data.

## Installation

First, clone or download the repository to your computer.

**Front End**- Navigate to the *www* directory and run `npm install`. Make sure you have the latest version of node.js installed on your computer.

**Back End**- The server should run with both python 2.7.x and 3.x. The only dependencies are numpy and flask, so just do a quick `pip install flask`, `pip install numpy`.

Finally, you'll want to create a `secrets.json` file of the form:

``
{
   "bittrex_key" : "mykey",
   "bittrex_secret" : "mysecret"
}
``

which you should save in the *backend/bot* directory. Now you're all set! Integration with more exchanges will be added soon.

## Running the Application

First, you'll need to use webpack to bundle all of the React .jsx files on the front end. Navigate to the *www* directory and run `npm run build`.

Next, navigate to the *backend* directory and run `python server.py`. Now you're all set! Open up your favorite browser and navigate to http://localhost:5000/ and try it out.

## How does it work?

First, you'll select the coin pair you want to trade with. 

"Capital" is the amount of BTC you want to start out with trading.

"Time Unit" is the duration of each point on the time series of historical data.

"Stop Loss" is the amount of BTC below each buy price that you will sell your position at. The smaller the stop loss, the less your risk.

"# Data Points" is the number of data points from the historical data to backtest on. It defaults to a value of "all", which processes all data points. Besides that, any positive integer value is valid for this field.

## What's on the Graph?

Green dots represent buy points. Red dots represent sell points. The blue line is the plot of historical closing prices, and the dotted yellow lines are Bollinger Bands. Moving averages will appear red and green, but this will be customizable later.

## Coming Soon

Strategy Panel, MACD plot, RSI plot

