import React from 'react';
import {Spinner} from 'spin.js';

import ControlPanel from './ControlPanel.jsx';
import Plot from './Plot.jsx';

class Dashboard extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
		    indicators: {
		        bollinger_upper: [],
                bollinger_lower: [],
                macd: [],
                rsi: [],
                movingaverage9: [],
                movingaverage15: []
            },
            closingPrices: [],
            buys: [],
            sells: [],
            profit: 0
        };


        this.state.coinPairs = ['ETH/BTC', 'LTC/BTC', 'XRP/BTC', 'XMR/BTC', 'NXT/BTC', 'BCC/BTC'];
        this.state.timeUnits = ['1m', '5m', '30m', '1h', '1d'];
        this.state.showIndicators = {'bollinger': true,
                                     'movingaverage9': false,
                                     'movingaverage15': false,
                                     'macd': false,
                                     'rsi': false};

        this.getBacktestingData = this.getBacktestingData.bind(this);
        this.onIndicatorChanged = this.onIndicatorChanged.bind(this);

        this.spinnerOpts = {
          lines: 13, // The number of lines to draw
          length: 38, // The length of each line
          width: 17, // The line thickness
          radius: 45, // The radius of the inner circle
          scale: 1, // Scales overall size of the spinner
          corners: 1, // Corner roundness (0..1)
          color: '#ffffff', // CSS color or array of colors
          fadeColor: 'transparent', // CSS color or array of colors
          opacity: 0.25, // Opacity of the lines
          rotate: 0, // The rotation offset
          direction: 1, // 1: clockwise, -1: counterclockwise
          speed: 1, // Rounds per second
          trail: 60, // Afterglow percentage
          fps: 20, // Frames per second when using setTimeout() as a fallback in IE 9
          zIndex: 2e9, // The z-index (defaults to 2000000000)
          className: 'spinner', // The CSS class to assign to the spinner
          top: '50%', // Top position relative to parent
          left: '50%', // Left position relative to parent
          shadow: 'none', // Box-shadow for the lines
          position: 'absolute' // Element positioning
        };

	}

    /** Executes when an indicator checkbox gets checked/unchecked
     *
     * @param indicator: The name of the indicator that was changed
     */
    onIndicatorChanged(indicator) {

    }

	 /** Retrieves backtesting results from the server
     *
     * @param coinPair: A trading pair whose historical data is to be retrieved
     * @param timeUnit: The time unit to extract from historical data (minute, hour, day, etc.)
     * @param capital: The amount of Bitcoin to start out with
     * @param period: The number of time units to grab
     * @param stopLoss: The amount of BTC below the initial buy position to set a stop loss at
     * @param buyStrategy: An object containing the buy strategy for this set of backtesting data
     * @param sellStrategy: An object containing the sell strategy for this set of backtesting data
     * @param indicators: An object containig key-value pairs of indicators and their parameters.
     */
	getBacktestingData(coinPair, timeUnit, capital, startTime, stopLoss, buyStrategy, sellStrategy, indicators) {
	    const url = "http://localhost:5000/backtest?pair=" + coinPair + "&period=" + timeUnit + "&capital=" + capital +
                    "&stopLoss=" + stopLoss + "&startTime=" + startTime;

	    const target = document.getElementById('d3plot');
        const spinner = new Spinner(this.spinnerOpts).spin(target);

	    $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: url,
            dataType: 'json',
            data: JSON.stringify({indicators: indicators, buyStrategy: buyStrategy, sellStrategy: sellStrategy}),
            success: data => {

                console.log("Got backtesting data:", data);

                const result = data['result'];

                this.setState({
                    coinPairs: this.state.coinPairs,
                    closingPrices: result['closingPrices'],
                    buys: result['buys'],
                    sells: result['sells'],
                    indicators: result['indicators'],
                    profit: result['profit']
                });
            },
            error: res => {
                document.getElementById('d3plot').innerHTML = "";
                swal("Uh oh!", "Something went wrong: Response code " + res.status + ". Please try again.", "error");
            }
        });
    }

	render() {
		return (
			<div id="dashboard">
			  <div className="row">
			    <ControlPanel getBacktestingData={this.getBacktestingData} coinPairs={this.state.coinPairs} profit={this.state.profit}
                    timeUnits={this.state.timeUnits} showIndicators={this.state.showIndicators} />
			  </div>

			  <Plot closingPrices={this.state.closingPrices} buys={this.state.buys} sells={this.state.sells}
                  indicators={this.state.indicators} showIndicators={this.state.showIndicators} />
			</div>
		)
	}
}

export default Dashboard;