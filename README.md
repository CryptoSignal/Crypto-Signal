# Crypto Signals

Development branch to testing new features. This develop version has a lot of improvements and fixes over master branch. The recommendation is that you use the code in this branch.

## Notable Changes
- It creates candle bar charts with MAs, RSI and MACD. These images can be sent as part of a Telegram notification or a Webhook call.
- It allows to include prices as part of the notification message.
- New configuration to easily add many coins. Check bellow for "all_pairs".
- New config var to use a custom "indicator_label" for each configured indicator and crossovers. Mainly useful for std_crossover.
- New indicator iiv (Increase In Volume) to try to identify a pump/dump.
- New indicator MA Ribbon
- New config values "hot_label" and "cold_label" for each indicator setup to set custom texts instead of the typical "hot" and "cold".
- New indicator ADX (Average Directional Index)
- New indicator Klinger Oscillator
- New indicator MACD Cross
- New indicator StochRSI Cross


## Installing And Running
Because this is a development branch you need to build your custom Docker image. The commands listed below are intended to be run in a terminal.

Be sure you have git installed in your system.

1. Clone this repo `git clone https://github.com/w1ld3r/crypto-signal.git`

1. Enter to cripto-signal folder `cd crypto-signal`

1. Switch to develop branch `git checkout develop`
 
1. Create a config.yml file and put it into "app" folder.

1. Build your own Docker image, for example, `docker build -t dev/crypto-signals:latest .`

1. For testing and debugging run docker with "-t" option `docker run --rm -ti -v  $PWD/app:/app dev/crypto-signals:latest`

1. For production run in daemon mode using "-d" option `docker run --rm -di -v  $PWD/app:/app dev/crypto-signals:latest`


### Configuring config.yml

All possible options for config.yml are almost the same for original CryptoSignal, so look [here](docs/config.md)

However there are some aditional options to use.

#### Mute cold

If the indicator you are using dispatch notifications for hot/cold signals you can use the "mute_cold" option to silence (mute) cold messages. Example:

```
indicators:
  rsi:
    - enabled: true
      alert_enabled: true
      alert_frequency: once
      signal:
        - rsi
      hot: 30
      cold: 70
      candle_period: 1d
      period_count: 14      
      mute_cold: true
```

#### Charts

You can enable/disable charts creation.

```
settings:
    log_level: INFO
    update_interval: 600
    enable_charts: true
    market_pairs:
        - XRP/USDT
        - ETH/USDT
        - BTC/USDT
        ....
```

#### All pairs

It is very useful to process all symbols of a specific base market (BTC, ETH, USD, USDT). In this way you can avoid to write pair by pair in settings.market_pairs option.

The all_pairs option must be specified by each exchange and base market. Example:

```
exchanges:
    binance:
        required:
            enabled: true
        all_pairs:
            - USDT
    bittrex:
        required:
            enabled: false
        all_pairs:
            - ETH
            - BTC
        ....
```

When using all_pairs we can exclude some pairs in particular. For example, in the following config, we are tracking all USDT pairs in Binance, except the other stable coins.

```
exchanges:
    binance:
        required:
            enabled: true
        all_pairs:
            - USDT
        exclude: 
          - USDC
          - PAX
          - BUSD            
    bittrex:
        required:
            enabled: false
        all_pairs:
            - ETH
        ....
```


#### Show me the price!

If you want prices in your notification messages, you can use the "prices" variable or "price_value".

```
notifiers:
    telegram:
        required:
            token: 791615820:AAGFgGSumWUrb-CyXtGxzAuYaabababababababa
            chat_id: 687950000
        optional:
            parse_mode: html
            template: "[{{analysis.config.candle_period}}] {{market}} {{values}} Prices: [{{prices}}]"
```

```
notifiers:
    telegram:
        required:
            token: 791615820:AAGFgGSumWUrb-CyXtGxzAuYaabababababababa
            chat_id: 687950000
        optional:
            parse_mode: html
            template: "[{{analysis.config.candle_period}}] {{market}} {{values}} Price 15m low: [{{price_value['15m'].low}}]"
```

By the way, to have this feature you need to configure "ohlcv" informant for each candle period of your indicators.

```
informants:
    ....
    bollinger_bands:
        - enabled: false
    ohlcv:
        - enabled: true
          signal:
            - high
            - low
            - close
          candle_period: 1h
          period_count: 14
        - enabled: true
          signal:
            - high
            - low
            - close
          candle_period: 4h
          period_count: 14
```

#### Candlestick Pattern Recognition - candle_recognition

Uses TA-LIB for candlestick pattern recognition
https://github.com/mrjbq7/ta-lib

* Set up `signal` for all candle patterns you want to check.
* Set up `candle_check` for how many candles you want to check. (default = 1 = checks last candle for pattern)
    For example your bot runs every 4 hours, but you want to check the candles of 1 hour, you can set it to trigger if the pattern happened on the last 4 candles
* Set up `notification` for what kind of notification you want when triggered, depending on what candle you check for. (default = hot)
* Possible to enable coloring on candle chart: allows for 5 different candles, priority coloring from up to down
* `Candle_check` allows for checking multiple candles for a pattern. [1=last candle, 2=last 2 candles etc]
    For example, if the program runs every 4 hours but you setup a candle recognition for 1 hour you can get a notification if there was a candle found in
    the last 4 candles by setting `candle_check:4`.

<details>
    <summary>possible signals</summary>

```
'two_crows': talib.CDLTRISTAR
'three_black_crows': talib.CDL3BLACKCROWS
'three_inside_up_down': talib.CDL3INSIDE
'three_line_strike': talib.CDL3LINESTRIKE
'thee_stars_in_the_south': talib.CDL3OUTSIDE
'three_advancing_white_soldiers': talib.CDL3WHITESOLDIERS
'abandoned_baby': talib.CDLABANDONEDBABY
'advance_block': talib.CDLADVANCEBLOCK
'belt_hold': talib.CDLADVANCEBLOCK
'breakaway': talib.CDLBREAKAWAY
'closing_marubozu': talib.CDLCLOSINGMARUBOZU
'concealing_baby_swallow': talib.CDLCONCEALBABYSWALL
'counterattack': talib.CDLCOUNTERATTACK
'dark_cloud_cover': talib.CDLDARKCLOUDCOVER
'doji': talib.CDLDOJI
'doji_star': talib.CDLDOJISTAR
'dragonfly_doji': talib.CDLDRAGONFLYDOJI
'engulfing_pattern': talib.CDLENGULFING
'evening_doji_star': talib.CDLEVENINGDOJISTAR
'evening_star': talib.CDLEVENINGSTAR
'gap_sidesidewhite': talib.CDLGAPSIDESIDEWHITE
'gravestone_doji': talib.CDLGRAVESTONEDOJI
'hammer': talib.CDLHAMMER
'hanging_man': talib.CDLHANGINGMAN
'harami_pattern': talib.CDLHARAMI
'harami_cross_patern': talib.CDLHARAMICROSS
'high_wave_candle': talib.CDLHIGHWAVE
'modified_hikkake_pattern': talib.CDLHIKKAKEMOD
'homing_pigeon': talib.CDLHOMINGPIGEON
'identical_three_crows': talib.CDLIDENTICAL3CROWS
'in_neck_pattern': talib.CDLINNECK
'inverted_hammer': talib.CDLINVERTEDHAMMER
'kicking': talib.CDLKICKING
'kicking_bb': talib.CDLKICKINGBYLENGTH
'ladder_bottom': talib.CDLLADDERBOTTOM
'long_legged_doji': talib.CDLLONGLEGGEDDOJI
'long_line_candle': talib.CDLLONGLINE
'marubozu': talib.CDLMARUBOZU
'matching_low': talib.CDLMATCHINGLOW
'mat_hold': talib.CDLMATHOLD
'morning_doji_star': talib.CDLMORNINGDOJISTAR
'morning_star': talib.CDLMORNINGSTAR
'on_neck_pattern': talib.CDLONNECK
'piercing_pattern': talib.CDLPIERCING
'rickshaw_man': talib.CDLRICKSHAWMAN
'risfall_three_methods': talib.CDLRISEFALL3METHODS
'seperating_lines': talib.CDLSEPARATINGLINES
'shooting_star': talib.CDLSHOOTINGSTAR
'short_line_candle': talib.CDLSHORTLINE
'spinning_top': talib.CDLSPINNINGTOP
'stalled_pattern': talib.CDLSTALLEDPATTERN
'stick_sandwich': talib.CDLSTICKSANDWICH
'takuri': talib.CDLTAKURI
'tasuki_gap': talib.CDLTASUKIGAP
'thrusting_pattern': talib.CDLTHRUSTING
'tristar_pattern': talib.CDLTRISTAR
'unique_three_river': talib.CDLUNIQUE3RIVER
'upside_gap_two_crows': talib.CDLUPSIDEGAP2CROWS
'xside_gap_three_methods': talib.CDLXSIDEGAP3METHODS
```
</details>

```
indicators:
  candle_recognition:
    - enabled: true
      alert_enabled: true
      alert_frequency: always
      signal:
        - doji
      candle_check: 1
      notification: hot
      candle_period: 1d
      hot: 0
      cold: 0
      chart: true
```

#### Aroon Oscillator - aroon_oscillator

The Aroon Oscillator is the difference between Aroon-Up and Aroon-Down. These two indicators are usually plotted together for easy comparison, but chartists can also view the difference between these two indicators with the Aroon Oscillator. This indicator fluctuates between -100 and +100 with zero as the middle line. An upward trend bias is present when the oscillator is positive, while a downward trend bias exists when the oscillator is negative. 

The Aroon Oscillator is positive AND daily volume was above the (default)50-day moving average of volume = hot notification
The Aroon Oscillator is negative AND daily volume was above the (default)50-day moving average of volume = cold notification


Periods in example are the default values

```
indicators:
  aroon_oscillator:
    - enabled: true
      alert_enabled: true
      alert_frequency: always
      sma_vol_period = 50
      period_count = 25
      signal:
        - aroon
      candle_period: 1d
      hot: 0
      cold: 0
```

#### Klinger Oscillator - klinger_oscillator

The Klinger oscillator (kvo) was developed by Stephen Klinger to determine the long-term trend of money flow
while remaining sensitive enough to detect short-term fluctuations. The indicator compares the volume
flowing through a security with the security's price movements and then converts the result into an oscillator.
The Klinger oscillator shows the difference between two moving averages which are based on more than price.
Traders watch for divergence on the indicator to signal potential price reversals.
Like other oscillators, a signal line can be added to provide additional trade signals.

If klinger signal line (kvo_signal) > 0 AND mean price is moving up from last candle = hot notification
If klinger signal line (kvo_signal) < 0 AND mean price is moving down from last candle = cold notification
mean price = (high + low + close) / 3

Periods in example are the default values

```
indicators:
  klinger_oscillator:
    - enabled: true
      alert_enabled: true
      alert_frequency: always
      ema_short_period = 34
      ema_long_period = 55
      signal_period = 13
      signal:
        - kvo
        - kvo_signal
      candle_period: 1d
```

#### Average Directional Index - adx

The Average Directional Movement Index (ADX) is designed to quantify trend strength by measuring the amount of price movement in a single direction. ADX is non-directional; it registers trend strength whether price is trending up or down
The ADX is part of the Directional Movement system published by J. Welles Wilder, and is the average resulting from the Directional Movement indicators.
ADX calculations are based on a moving average of price range expansion over a given period of time. The default setting is 14 bars, although other time periods can be used. 
When the +DMI(pdi) is above the -DMI(ndi), prices are moving up, and ADX measures the strength of the uptrend. When the -DMI(ndi) is above the +DMI(pdi), prices are moving down, and ADX measures the strength of the downtrend.

0-25 absent or weak trend
25-50 strong trend
50-75 very strong trend
75-100 extremely strong trend

```
indicators:
  adx:
    - enabled: true
      alert_enabled: true
      alert_frequency: always
      signal:
        - adx
        - pdi
        - ndi
      hot: 50
      cold: 25
      candle_period: 1d
      period_count: 14
```

#### Increase In Volume indicator - iiv

There is a new indicator called "iiv" enabled for default for 5m period. The hot value is 5 by default, you can adjust it as you want, may be 10 o 15. This value is a measure about how strong is the increase in volume.

The main idea is to try to identify a possible pump or dump.

```
indicators:
  iiv:
    - enabled: true
      alert_enabled: true
      alert_frequency: always
      signal:
        - iiv
      hot: 5
      cold: 0
      candle_period: 5m
```

If you don't want to receive such notifications just disable the iiv indicator in your config file.

```
indicators:
  iiv:
    - enabled: false
      candle_period: 5m
```

Of course, this indicator can be used in other candle periods, 15m, 1h.. etc.

#### Moving Average Ribbon

First, read the following link to know about what it is: 
https://www.investopedia.com/terms/m/movingaverageribbon.asp

Second, the code used to implement this indicator was taken from another proyect called pyktrader2. It is not my own and therefore 
I don't know the details about how this indicator works, so what I comment below is what I think it is. 

```
indicators:
    ma_ribbon:
        - enabled: true
          alert_enabled: true
          alert_frequency: always
          signal:
            - pval
            - corr
          hot: 10
          cold: -10
          hot_label: 'Uptrend is coming'
          cold_label: 'Downtred is coming'
          candle_period: 15m
          pval_th: 20
          ma_series: 5, 15, 25, 35, 45
```

The "corr" value changes from -100 to 100. When corr starts increasing from 0 to 100 we talk of an possible Uptrend, when corr goes from 0 to -100 we are entering in a Downtrend. The "hot" and "cold" values in config file are associated with such corr.

To confirm the change in trend, the "pval" is used. This value changes from 0 to 100, but, when this value approaches 0 it confirms the signal given by corr.

The "ma_series" config value is used to set the moving averages that will be used by the indicator.

#### Moving Average Crossover

It is a new indicator created with the idea of making the configuration of MA crossovers simpler and clearer. It is called "ma_crossover" and is configured into "indicators" section.

```
indicators:
    ma_crossover:
        - enabled: true
          candle_period: 1h
          alert_enabled: true
          alert_frequency: once
          exponential: true
          ma_fast: 50
          ma_slow: 100
          signal:
            - open
            - close
          hot_label: 'Uptrend is coming'
          cold_label: 'Downtred is coming'
          indicator_label: 'EMA 50/100 Cross'
```

The three basic values to configure are "exponential", "ma_slow" and "ma_fast". The "exponential" value is a true/false value indicating when to use Exponential Moving Average. If false, Simple Moving Average will be used. 

"ma_fast" is the number of periods to use for the fast line, and "ma_slow" is the number of periods to use for the slow line.

"signal" isn't really a meaning value for this indicator, but we have to set something because the code base requires that parameter for all indicators. So we can simply set some ohlcv value to avoid an error config.

#### Bollinger

It is a new indicator created to easily get alerts when the close price crosses the Up/Low bands calculated for the Bollinger Bands. It is different of the Bollinger informant, and therefore it is configured in the "indicators" section.

```
indicators:
    bollinger:
        - enabled: true
          candle_period: 1h
          alert_enabled: true
          alert_frequency: once
          period_count: 20
          std_dev: 2
          signal:
            - low_band
            - close
            - up_band
          hot_label: 'Lower Band'
          cold_label: 'Upper Band'
          indicator_label: 'Bollinger Crossing'
          mute_cold: false
```

The most important config is the number of standar deviations to use. Tipically values are 2 and 1.

#### Percent B (%B)

The Percent B indicator reflects closing price as a percentage of the lower and upper Bollinger Bands. The idea is almost the same as Bollinger indicator, to get alerts when the close price crosses the Up/Low bands. 

```
indicators:
    bbp:
        - enabled: true
          candle_period: 1h
          alert_enabled: true
          alert_frequency: once
          period_count: 20
          hot: 0
          cold: 0.8  
          std_dev: 2
          signal:
            - bbp
            - mfi
          hot_label: 'Lower Band'
          cold_label: 'Upper Band'
          indicator_label: 'Bollinger Crossing'
          mute_cold: false
```


#### MACD Cross

The existing "macd" indicator always sends hot signals when the macd > 0, and cold signals when macd < 0. I repeat, always. Perhaps this is not the desired behavior and you only want to receive notifications when macd crosses the signal line, then this new MACD Cross indicator is the appropriate.

```
indicators:
  macd_cross:
    - enabled: true
      candle_period: 4h
      alert_enabled: true
      alert_frequency: always
      signal:
        - macd
        - signal
      hot_label: 'Uptrend is coming'
      cold_label: 'Downtred is coming'
      indicator_label: 'MACD Cross 4h'
      mute_cold: false
```
#### StochRSI Cross

This indicator is useful if you are interested in knowing when smooth K line crosses the smooth D line of the StochRSI. Unlike the StochRSI indicator, this new indicator allows you to set values ​​for K and D.

```
indicators:
  stochrsi_cross:
    - enabled: true
      candle_period: 4h
      alert_enabled: true
      alert_frequency: always
      smooth_k: 10
      smooth_d: 3
      signal:
        - stoch_rsi
        - smooth_k
        - smooth_d
      hot_label: 'Uptrend is coming'
      cold_label: 'Downtred is coming'
      indicator_label: 'StochRSI Cross 4h'
      mute_cold: false
```

#### Chart images on webhook

The config for a webhook notifier is the same as original CryptoSignal, no changes here, BUT the data sent in the request is completely different. 

```
notifiers:
    telegram:
        required:
            token: 791615820:AAGFgGSumWUrb-CyXtGxzAuY7UPxxxxx
            chat_id: 687957000
        optional:
            parse_mode: html
            template: "[{{indicator_label}}] {{market}} {{values}}, Prices: [{{prices}}]" 
    webhook:
        required:
            url: http://somename.or.ip.here:8888/someuri
        optional:
            username: null
            password: null    
```

Then in your webhook you will have a parameter "messages" which is a list/array of the notification messages in form of string values. Apply a json decode to access all values. In python pseudo code:

```
msg = self.get_argument('messages')
print ( json.loads(msg) )
        
[{'values': {'rsi': '84.20'}, 'exchange': 'binance', 'market': 'VET/USDT', 'base_currency': 'VET', 'quote_currency': 'USDT', 'indicator': 'rsi', 'indicator_number': 0, 'analysis': {'config': {'enabled': True, 'alert_enabled': True, 'alert_frequency': 'always', 'signal': ['rsi'], 'hot': 40, 'cold': 60, 'candle_period': '15m', 'period_count': 13}, 'status': 'cold'}, 'status': 'cold', 'last_status': 'cold', 'creation_date': '2019-01-04 15:31:40', 'indicator_label': 'rsi 15m'}]
```

If you have enable_charts: true, you will have a parameter "chart" in the same way of a HTTP file upload. Reading this file depends 100% in your backend. Example python pseudo code to save the received chart:

```
    fileinfo = self.request.files['chart'][0]
        
    print ("filename is " , fileinfo['filename'], ', content_type: ', fileinfo['content_type'])

    fname = fileinfo['filename']
    extn = os.path.splitext(fname)[1]
    cname = str(uuid.uuid4()) + extn
    fh = open(__UPLOADS__ + cname, 'wb')
    fh.write(fileinfo['body'])
```

### Custom Hot/Cold labels

Setting a custom text for the "hot" or "cold" signals allows to have a really cool notification message.

```
indicators:
    rsi:
        - enabled: true
          alert_enabled: true
          alert_frequency: always
          signal:
            - rsi
          hot: 40
          cold: 60
          hot_label: We Are In Oversold!
          cold_label: Attention! Overbought!
          candle_period: 1h
          period_count: 13
```

So, in the message template the "hot_cold_label" variable will have one of the two possible values.

```
template: "[{{indicator_label}}] **{{hot_cold_label}}** {{market}}  Prices: [{{prices}}]"  
```


### Price Values

To use this feature it is necessary to configure "ohlcv" informant for each candle period of your indicators. For example, this config is used to get High, Low and Close prices for 1h and 4h indicators.

```
informants:
    ....
    bollinger_bands:
        - enabled: false
    ohlcv:
        - enabled: true
          signal:
            - high
            - low
            - close
          candle_period: 1h
          period_count: 14
        - enabled: true
          signal:
            - high
            - low
            - close
          candle_period: 4h
          period_count: 14  
```

Then you can use the "price_value" variable to have the values of prices and be able to do some operations on them.

```
notifiers:
    telegram:
        required:
            token: 580514307:AAETsNsxs4QCdyEZ59vVROLlBxxxxx
            chat_id: 2073900000
        optional:
            parse_mode: html
            template: "{{ market }} 
            BUY {{ price_value['1h'].close }} 
            SL: {{ decimal_format|format(price_value['4h'].low * 0.9) }} 
            TP: {{ decimal_format|format(price_value['1h'].close * 1.02) }} {{ decimal_format|format(price_value['4h'].close * 1.04) }} "
```

The code for "decimal_format" and "format" is necessary to obtain the prices formatted with the corresponding zeros.
