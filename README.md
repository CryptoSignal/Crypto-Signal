# Crypto Signals

Development branch to testing new features. If you are looking for the latest stable version check the master branch.

## Notable Changes
- It creates candle bar charts with MAs, RSI and MACD. These images can be sent as part of a Telegram notification or a Webhook call.
- It allows to include prices as part of the notification message.
- New configuration to easily add many coins. Check bellow for "all_pairs".
- New config var to use a custom "indicator_label" for each configured indicator and crossovers. Mainly useful for std_crossover.
- New indicator iiv (Increase In Volume) to try to identify a pump/dump.
- New indicator MA Ribbon
- New config values "hot_label" and "cold_label" for each indicator setup to set custom texts instead of the typical "hot" and "cold".

## Installing And Running
Because this is a development branch you need to build your custom Docker image. The commands listed below are intended to be run in a terminal.

Be sure you have git installed in your system.

1. Clone this repo `git clone https://github.com/CryptoSignal/crypto-signal.git`

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

Finally, if you want prices in your notification messages, you can use a new variable "prices".

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

Because this indicator is commonly used in conjunction with MFI indicator, such signal has been added as part of the configuration. This way, the values of both indicators can be read together. 

Important: For this indicator the hot/cold config values are mandatory.

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
