import React from 'react';

class ControlPanel extends React.Component {

   constructor(props) {
       super(props);

       this.setupMaterializePlugins = this.setupMaterializePlugins.bind(this);
       this.requestBacktest = this.requestBacktest.bind(this);
       this.getStrategies = this.getStrategies.bind(this);
       this.addCondition = this.addCondition.bind(this);
       this.removeCondition = this.removeCondition.bind(this);

       this.state = {conditions: {
           buy: [1],
           sell: [1]
       }};

       this.acceptableIndicators = {"Current Price": "currentprice",
                                    "Moving Average (9 Period)": "movingaverage9",
                                    "Moving Average (15 Period)": "movingaverage15",
                                    "RSI": "rsi"};
   }

   render() {

       const showIndicators = this.props.showIndicators;

       const indicatorDropdown = (id) =>
                            <select id={id} className="indicator-dropdown">
                               <option value="" disabled defaultValue>Choose an indicator...</option>
                                 <option value="currentprice">Current Price</option>
                                 <option value="movingaverage9">Moving Average (9 Period)</option>
                                 <option value="movingaverage15">Moving Average (15 Period)</option>
                                 <option value="rsi">RSI</option>
                             </select>;

       const indicatorValue = (id) => <div>
                                      <input id={id} placeholder="" type="text" className="autocomplete" />
                                      <label htmlFor={id}>Value</label>
                                    </div>;

       const comparator = (id) =>
                          <select id={id} className="comparator">
                               <option value="" disabled defaultValue>Choose...</option>
                               <option value="LT">&lt;</option>
                               <option value="EQ">=</option>
                               <option value="GT">&gt;</option>
                          </select>;

       const coinFields = <div>
                            <div className="row">
                             <div className="input-field col s6">
                             <select id="coin-pair">
                               <option value="" disabled defaultValue>Pick a coin pair...</option>
                                 { this.props.coinPairs.map(pair =>
                                     <option key={pair} value={pair}>{pair}</option>
                                 )}
                             </select>
                             <label>Coin Pair</label>
                             </div>
                             <div className="input-field col s6">
                               <input placeholder="Eg: 0.01" id="amount-btc" type="text" className="validate" />
                               <label className="active" htmlFor="amount-btc">Capital</label>
                             </div>
                            </div>
                            <div className="row">
                             <div className="input-field col s4">
                               <select id="time-unit">
                               <option value="" disabled defaultValue>Pick a time unit...</option>
                                 { this.props.timeUnits.map(unit =>
                                     <option key={unit} value={unit}>{unit}</option>
                                 )}
                               </select>
                               <label>Time Unit</label>
                             </div>
                             <div className="input-field col s4">
                               <input defaultValue="0" id="stop-loss" type="text" className="validate" />
                               <label className="active" htmlFor="stop-loss">Stop Loss</label>
                             </div>
                             <div className="input-field col s4">
                               <input defaultValue="all" id="num-data" type="text" className="validate" />
                               <label className="active" htmlFor="num-data"># Data Points</label>
                             </div>
                            </div>
                           </div>;

       const strategyFields = <div className="input-field col s12 strategy-container">
                             { this.state.conditions.buy.map(index =>
                                 <div key={`buyrow-${index}`} className="row">
                                 <div className="input-field col s5">
                                     { indicatorDropdown(`buy-field-${index}`) }
                                 <label>Buy When</label>
                                 </div>
                                 <div className="input-field col s2">
                                     { comparator(`buy-comparator-${index}`) }
                                 </div>
                                 <div className="input-field col s5">
                                     {/*{ indicatorDropdown("buy-value") }*/}
                                     { indicatorValue(`buy-value-${index}`) }
                                 </div>
                                 </div>
                             )}

                             <div className="row">
                                 <a onClick={() => this.addCondition('BUY')} className="btn btn-small btn-floating waves-effect waves-light">
                                     <i className="material-icons">add</i>
                                 </a>

                                 <a disabled={this.state.conditions.buy.length == 1} onClick={() => this.removeCondition('BUY')} className="btn btn-small btn-floating waves-effect waves-light right">
                                     <i className="material-icons">remove</i>
                                 </a>
                             </div>

                             { this.state.conditions.sell.map(index =>
                                 <div key={`sellrow-${index}`} className="row">
                                 <div className="input-field col s5">
                                     { indicatorDropdown(`sell-field-${index}`) }
                                 <label>Sell When</label>
                                 </div>
                                 <div className="input-field col s2">
                                     { comparator(`sell-comparator-${index}`) }
                                 </div>
                                 <div className="input-field col s5">
                                     {/*{ indicatorDropdown("sell-value") }*/}
                                     { indicatorValue(`sell-value-${index}`) }
                                 </div>
                                 </div>
                             )}

                             <div className="row">
                                 <a onClick={() => this.addCondition('SELL')} className="btn btn-small btn-floating waves-effect waves-light">
                                     <i className="material-icons">add</i>
                                 </a>

                                 <a disabled={this.state.conditions.sell.length == 1} onClick={() => this.removeCondition('SELL')} className="btn btn-small btn-floating waves-effect waves-light right">
                                     <i className="material-icons">remove</i>
                                 </a>
                             </div>


                           </div>;

       const indicatorCheckboxes = <form action="#">
                            <p>
                              <input type="checkbox" id="bbands-box" defaultChecked={showIndicators.bollinger} />
                              <label htmlFor="bbands-box">Bollinger Bands</label>
                            </p>
                            <p>
                              <input type="checkbox" id="ma-9-box" defaultChecked={showIndicators.movingaverage9} />
                              <label htmlFor="ma-9-box">Moving Average (9 Period)</label>
                            </p>
                            <p>
                              <input type="checkbox" id="ma-15-box" defaultChecked={showIndicators.movingaverage15} />
                              <label htmlFor="ma-15-box">Moving Average (15 Period)</label>
                            </p>
                            <p>
                              <input type="checkbox" id="macd" defaultChecked={showIndicators.macd} />
                              <label htmlFor="macd">MACD</label>
                            </p>
                            <p>
                              <input type="checkbox" id="rsi" defaultChecked={showIndicators.rsi} />
                              <label htmlFor="rsi">Relative Strength Index</label>
                            </p>
                          </form>;

       return (
		    <div className="row">
                <div className="col s12 m12">
                  <div className="card light-blue accent-3">
                    <div className="card-content white-text">
                        <div className="row">
                          <div className="col s6 m4">
                            <span className="card-title">Coin Information</span>
                            { coinFields }
                          </div>
                          <div className="col s6 m5 strategy">
                            <span className="card-title">Strategy</span>
                            { strategyFields }
                          </div>
                          <div className="col s6 m3">
                            <span className="card-title">Plot</span>
                            { indicatorCheckboxes }
                          </div>
                        </div>
                    </div>
                    <div className="card-action">
                      <a onClick={this.requestBacktest} className="waves-effect waves-light btn btn-small">Begin</a>
                      <h5 className="right white-text">Profit: {this.props.profit} BTC</h5>
                    </div>
                  </div>
                </div>
            </div>
       )
   }

   setupMaterializePlugins() {
       // Activate the dropdowns when the compoment mounts
       $('select').material_select();

       // Activate autocomplete when the component mounts (setTimeout hack)
       setTimeout(() => $('.autocomplete').autocomplete({
           data: {
               "Current Price": null,
               "Moving Average (9 Period)": null,
               "Moving Average (15 Period)": null,
               "RSI": null
           },
           minLength: 0
       }), 200);
   }

   componentDidMount() {
       this.setupMaterializePlugins();
   }

   componentDidUpdate() {
       this.setupMaterializePlugins();
   }

   requestBacktest() {
       const coinPair = $('#coin-pair').val();
       const timeUnit = $('#time-unit').val();
       const capital = $('#amount-btc').val();
       const stopLoss = $('#stop-loss').val();
       let length = $('#num-data').val();

       if (length == 'all') {
           length = 999999;
       }

       let indicators = {
           'movingaverage': []
       };

       if ($('#bbands-box').is(':checked')) {
           indicators['bollinger'] = 21;
       }

       if ($('#ma-9-box').is(':checked')) {
           indicators['movingaverage'].push(9);
       }

       if ($('#ma-15-box').is(':checked')) {
           indicators['movingaverage'].push(15);
       }

       const [buyStrategy, sellStrategy] = this.getStrategies();


       this.props.getBacktestingData(coinPair, timeUnit, capital, length, stopLoss, buyStrategy, sellStrategy, indicators);
   }

   getStrategies() {
       const buyConditions = this.state.conditions.buy;
       const sellConditions = this.state.conditions.sell;

       let buy_strategy = {};
       let sell_strategy = {};

       for (let i = 1; i <= buyConditions.length; i++) {
           let [buyField, buyComp, buyVal] = [$(`#buy-field-${i}`).val(), $(`#buy-comparator-${i}`).val(), $(`#buy-value-${i}`).val()];

           if (isNaN(buyVal)) {

               if (!(buyVal in this.acceptableIndicators)) {
                   swal("Uh oh!", "You must enter a number or one of the suggested indicators.", "error");
                   throw "Incorrect value for buy field";
               }

               buyVal = this.acceptableIndicators[buyVal];

           }
           buy_strategy[buyField] = {'comparator': buyComp, 'value': isNaN(buyVal) ? buyVal : +buyVal};
       }

       for (let i = 1; i <= sellConditions.length; i++) {
           let [sellField, sellComp, sellVal] = [$(`#sell-field-${i}`).val(), $(`#sell-comparator-${i}`).val(), $(`#sell-value-${i}`).val()];

           if (isNaN(sellVal)) {

               if (!(sellVal in this.acceptableIndicators)) {
                   swal("Uh oh!", "You must enter a number or one of the suggested indicators.", "error");
                   throw "Incorrect value for sell field";
               }

               sellVal = this.acceptableIndicators[sellVal];

           }
           sell_strategy[sellField] = {'comparator': sellComp, 'value': isNaN(sellVal) ? sellVal : +sellVal};
       }

       console.log(buy_strategy, sell_strategy);
       return [buy_strategy, sell_strategy];
   }

   addCondition(buyOrSell) {
       // Make a deep clone of the state so it activates our component lifecycle methods
       const conditions = JSON.parse(JSON.stringify(this.state.conditions));

       if (buyOrSell == 'BUY') {
           conditions.buy.push(conditions.buy.length + 1);
           this.setState({conditions: conditions});
       } else if (buyOrSell == 'SELL') {
           conditions.sell.push(conditions.sell.length + 1);
           this.setState({conditions: conditions});
       }
   }

   removeCondition(buyOrSell) {
       // Make a deep clone of the state so it activates our component lifecycle methods
       const conditions = JSON.parse(JSON.stringify(this.state.conditions));

       if (buyOrSell == 'BUY') {
           conditions.buy.pop();
           this.setState({conditions: conditions});
       } else if (buyOrSell == 'SELL') {
           conditions.sell.pop();
           this.setState({conditions: conditions});
       }
   }

}


export default ControlPanel;