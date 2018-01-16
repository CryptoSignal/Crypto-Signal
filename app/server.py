from flask import Flask, request, jsonify, render_template
from backtesting.backtest import Backtester

app = Flask(__name__, static_folder='../www/static', template_folder='../www/static/templates')

# Add a rotating file handler to keep track of error logging
if app.debug is not True:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('errors.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/backtest", methods=['POST'])
def backtesting():

    coin_pair = request.args.get('pair')
    period_length = request.args.get('period')
    capital = float(request.args.get('capital'))
    stop_loss = float(request.args.get('stopLoss'))
    start_time = int(request.args.get('startTime'))

    post_data = request.get_json()
    indicators = post_data['indicators']
    buy_strategy = post_data['buyStrategy']
    sell_strategy = post_data['sellStrategy']

    # TODO: Change 'bittrex' to an arbitrary exchange passed in by query params
    backtester = Backtester(coin_pair, period_length, 'bittrex', capital, stop_loss, start_time, buy_strategy, sell_strategy, indicators)
    backtester.run()
    result = backtester.get_results()

    # result = backtest(coin_pair, period_length, capital, stop_loss, num_data, buy_strategy, sell_strategy, indicators)

    return jsonify(response=200, result=result)


if __name__ == '__main__':
    app.run(debug=True)
