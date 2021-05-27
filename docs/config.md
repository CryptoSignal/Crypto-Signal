# Table of Contents

1) Configuration file structure
2) Settings
3) Exchanges
4) Notifiers
5) Indicators
6) Informants
7) Crossovers
8) Examples

# 1) Configuration file structure
The configuration file is YAML formatted and consists of the following top level keys.

- settings
- exchanges
- notifiers
- indicators
- informants
- crossovers

You will find a detailed description of each key below

# 2) Settings
General settings for crypto-signal

**log_mode**\
default: text\
necessity: optional\
description: Can be set to `text`, `json` or `standard`. This will specify the log format for events emitted by the logger.

**log_level**\
default: INFO\
necessity: optional\
description: Can be set to `DEBUG`, `INFO`, `WARN`, `ERROR`. Used to set the logger verbosity.

**output_mode**\
default: cli\
necessity: optional\
description: This option is deprecated and will be removed in a later version. Can be set to `cli`, `csv` or `json`. This will specify the output format for events emitted by the app.

**update_interval**\
default: 300\
necessity: optional\
description: This option controls how frequently to rescan the exchange information (in seconds).

**market_pairs**\
default: None\
necessity: optional\
description: Allows you to specify a list of market pairs you are interested in.

An example of settings in the config.yml file might look like

```yml
settings:
  log_mode: text
  log_level: INFO
  output_mode: cli
  update_interval: 300
  market_pairs:
    - ETH/BTC
    - LTC/BTC
    - XMR/BTC
```

# 3) Exchanges
Settings that alter behaviour of interaction with an exchange.

**enabled**\
default: False\
necessity: required\
description: Valid options are `true` or `false`. This setting enables or disables exchanges.

An example of exchange settings

```yml
exchanges:
    bittrex:
        required:
            enabled: true
```

# 4) Notifiers
Settings to configure what services to notify when a hot or cold threshold is tripped.

## Twilio
**key**\
default: None\
necessity: required for Twilio\
description: The twilio API key required for communication.

**secret**\
default: None\
necessity: required for Twilio\
description: The twilio API key secret required for communication.

**sender_number**\
default: None\
necessity: required for Twilio\
description: The twilio phone number for sending the message.

**receiver_number**\
default: None\
necessity: required for Twilio\
description: The receiving phone number (your phone number) for receiving the message.

**template**\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

An example of notifier settings for twilio

```yml
notifiers:
    twilio:
        required:
            key: abcd1234
            secret: abcd1234
            sender_number: 123456789
            receiver_number: 123456789
        optional:
            template: "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
```

## Slack
**webhook**\
default: None\
necessity: required for Slack\
description: The Slack webhook required for sending messages.

**template**\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

An example of notifier settings for slack

```yml
notifiers:
    slack:
        required:
            webhook: https://abcd1234
        optional:
            template: "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
```

## Email
**smtp_server**\
default: None\
necessity: required for Email\
description: Your smtp server hostname

**username**\
default: None\
necessity: required for Email\
description: Your email username which is required for sending emails.

**password**\
default: None\
necessity: required for Email\
description: Your email password which is required for sending emails.

**destination_emails**\
default: None\
necessity: required for Email\
description: The email addresses to receive the emails that are sent.

**template**\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

An example of notifier settings for email

```yml
notifiers:
    email:
        required:
            smtp_server: smtp.gmail.com:587
            username: example@gmail.com
            password: abcd1234
            destination_emails:
                - my_user@gmail.com
        optional:
            template: "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
```

## Telegram
**token**\
default: None\
necessity: required for Telegram\
description: Your telegram bot token you can generate a token by following the instructions [here](https://core.telegram.org/bots#6-botfather)

**chat_id**\
default: None\
necessity: required for Telegram\
description: The chat_id to send the message too. The easiest way to get get this id is probably using RawDataBot or Userinfobot.

**parse_mode**\
default: html\
necessity: optional\
description: Valid options are html or markdown. Choose what text formatting parser to use.

**template**\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

An example of notifier settings for telegram

```yml
notifiers:
    telegram:
        required:
            token: abcd1234
            chat_id: abcd1234
        optional:
            parse_mode: html
            template: "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
```

## Discord
**webhook**\
default: None\
necessity: required for Discord\
description: The Discord webhook REQUIRED for sending messages.

**username**\
default: None\
necessity: required for Discord\
description: The Discord username that will be sending messages. Can be anything.

**avatar**\
default: None\
necessity: optional for Discord\
description: The Discord avatar image for the username sending messages. Set to None for default pokemon.

**template**\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

An example of notifier settings for discord

```yml
notifiers:
    discord:
        required:
            webhook: http://abcd1234
            username: abcd1234
        optional:
            avatar: http://abcd1234/avatar.png
            template: "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
```

## Webhook
**url**\
default: None\
necessity: required for webhook\
description: The URL to send the json payload to.

**username**\
default: None\
necessity: optional for webhook\
description: The username for basic authentication if required.

**password**\
default: None\
necessity: optional for webhook\
description: The password for basic authentication if required.

An example of notifier settings for webhook

```yml
notifiers:
    webhook:
        required:
            url: http://abcd1234
        optional:
            username: abcd1234
            password: abcd1234
```

## StdOut
**enable**\
default: None\
necessity: required for StdOut\
description: switches on the output via stdout

**template**\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

An example of notifier settings for stdout. This will just print the notification to stdout.
Usefull for testing

```yml
notifiers:
    stdout:
        required:
            enable: true
        optional:
            template: "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
```

## Notifier Templating
The notifier templates are built with a templating language called [Jinja2](http://jinja.pocoo.org/docs/2.10/templates/) and anything that is a valid Jinja message is valid for crypto-signal. The options available are as follows:

- exchange - The name of the exchange for the indicator.
- market - The name of the market for the indicator.
- base_currency - The name of the base currency. If the market is BTC/USD, then this value is BTC.
- quote_currency - The name of the quote currency. If the market is BTC/USD, then this value is USD.
- indicator - The name of the analyzer used for this indicator.
- indicator_number - Which configured instance of the analyzer this indicator applies too.
- status - Whether the indicator is hot, cold or neutral.
- last_status - The status of the previous analysis run.
- values.<signal> - The stringified value from the selected signal line, see the indicator section for the signal lines available for each indicator.
- analysis.result.<signal> - The raw value from the selected signal line, see the indicator section for the signal lines available for each indicator.
- analysis.result.is_hot - The raw boolean value of if the indicator is hot.
- analysis.result.is_cold - The raw boolean value of if the indicator is cold.
- analysis.config.enabled - The raw config item of if this indicator is enabled. If you receive a message with a value other than True something has gone horribly wrong.
- analysis.config.alert_enabled - The raw config item of if this indicator alert is enabled. If you receive a message with a value other than True something has gone horribly wrong.
- analysis.config.alert_frequency - The raw config item of whether this alert is always sent or if it is only sent once per status change.
- analysis.config.hot - The raw config item of what the configured hot threshold is.
- analysis.config.cold - The raw config item of what the configured cold threshold is.
- analysis.config.candle_period - The raw config item of what time period of candles to gather.
- analysis.config.period_count - The raw config item of how many candles to gather.
- analysis.config.signal - The raw config item of the configured signal lines.

As an example of how to use it, lets say you want to write a custom message for discord... it would end up looking something like...

```
template: "[{{analysis.config.candle_period}}] {{market}} on {{exchange}} is {{status}}"
```

The result of the above custom template would generate a message that looks like: [1h] BURST/BTC on bittrex is hot.

# 5) Indicators

**enabled**\
default: True\
necessity: optional\
description: Valid values are true or false. Whether to perform analysis on this indicator.

**alert_enabled**\
default: True\
necessity: optional\
description: Valid values are true or false. Whether to send alerts for this particular indicator.

**signal**\
default: A string\
necessity: optional\
description: Valid values are on a per indicator basis see the table below. Each indicator may have a variety of signal lines, this option allows you to specify which options you care about. The first one specified is used for determining hot/cold the others are just output to the cli for information. Valid options are:

```
KLINGER OSCILLATOR - kvo, kvo_signal
ADX - adx
MOMENTUM - momentum
RSI - rsi
MACD - macd, macdsignal, macdhist
ICHIMOKU - leading_span_a, leading_span_b
STOCHASTIC_RSI - stoch_rsi, slow_k, slow_d
MFI - mfi
OBV - obv
```

**hot**\
default:\
necessity: optional\
description: A valid option must be an integer or float. This is the number at which you want this indicator to become hot. For some indicators that is when it is above a threshold and for some it is below a threshold... this is automatically handled by the indicator you just need to provide the value.

**cold**\
default:\
necessity: optional\
description: A valid option must be an integer or float. This is the number at which you want this indicator to become cold. For some indicators that is when it is above a threshold and for some it is below a threshold... this is automatically handled by the indicator you just need to provide the value.

**candle_period**\
default: 1d\
necessity: optional\
description: Valid options vary by exchange, common options include 1m, 5m, 1h, 4h, 1d. This dictates what granularity of rollup to use for the analyzed candles, so a candle period of 1d will roll the candles up to 1 day blocks.

**period_count**\
default: An integer\
necessity: optional\
description: Valid options are an integer. This is the count of candle periods to use for this analysis. Let's suppose you wanted to test 15 days of RSI data. You would set the `candle_period: 1d` and then set `period_count: 15`, which means 15 counts of 1d periods, or in other words 15 days.

This option is only supported by the following indicators: adx, momentum, mfi, rsi, stoch_rsi


An example of configuring an indicator would look as follows:

```yml
indicators:
    momentum:
        - enabled: true
          alert_enabled: true
          alert_frequency: once
          signal:
            - momentum
          hot: 0
          cold: 0
          candle_period: 1d
          period_count: 10
```

# 6) Informants

**enabled**\
default: True\
necessity: optional\
description: Valid values are true or false. Whether to perform analysis on this indicator.

**signal**\
default: A string\
necessity: optional\
description: Valid values are on a per indicator basis see the options in the table at the start of the analyzers section for a full list of what is available. Each indicator may have a variety of signal lines, this option allows you to specify which options you care about. Valid options are:

```
SMA - sma
EMA - ema
VWAP - vwap
BOL_BAND - upperband, middleband, lowerband
OHLCV - open, high, low, close, volume
```

**period_count**\
default: An integer\
necessity: optional\
description: Valid options are an integer. This is the count of candle periods to use for this analysis. Let's suppose you wanted to test 15 days of EMA data. You would set the `candle_period: 1d` and then set `period_count: 15`, which means 15 counts of 1d periods, or in other words 15 days.


An example of configuring an informant would look as follows:

```yml
informants:
    vwap:
        - enabled: true
          signal:
            - vwap
          candle_period: 1d
          period_count: 15
```

# 7) Crossovers

**enabled**\
default: False\
necessity: optional\
description: Valid values are true or false. Whether to perform analysis on this indicator.

**alert_enabled**\
default: False\
necessity: optional\
description: Valid values are true or false. Whether to send alerts for this particular indicator.

**key_indicator**\
default: N/A\
necessity: optional\
description: Valid values are the name of any indicator or informant. The indicator that gets hot when it goes above the crossed indicator and cold when it goes below it.

**key_indicator_index**\
default: N/A\
necessity: optional\
description: Valid values are positive integers. The index of the selected key indicator or informant that you want to use.

**key_indicator_type**\
default: N/A\
necessity: optional\
description: Valid values are 'indicators' or 'informants'. Whether the key indicator is of type informant or indicator.

**key_signal**\
default: N/A\
necessity: optional\
description: Valid values are the name of a signal line for the select indicator or informant. Which signal to use of the selected indicator or informant.

**crossed_indicator**\
default: N/A\
necessity: optional\
description: Valid values are the name of any indicator or informant. The indicator or informant that the key indicator is intended to cross.

**crossed_indicator_index**\
default: N/A\
necessity: optional\
description: Valid values are positive integers. The index of the selected crossed indicator or informant that you want to use.

**crossed_indicator_type**\
default: N/A\
necessity: optional\
description: Valid values are 'indicators' or 'informants'. Whether the crossed indicator is of type informant or indicator.

**crossed_signal**\
default: N/A\
necessity: optional\
description: Valid values are the name of a signal line for the select indicator or informant. Which signal to use of the selected indicator or informant.


An example of configuring an informant would look as follows:

```yml
crossovers:
    std_crossover:
        - enabled: false
          alert_enabled: true
          alert_frequency: once
          key_indicator: ema
          key_indicator_index: 0
          key_indicator_type: informants
          key_signal: ema
          crossed_indicator: sma
          crossed_indicator_index: 0
          crossed_indicator_type: informants
          crossed_signal: sma
```

# 8) Conditionals

It's allowing you to receive notifications, only if one or more conditions are respected.

Use case examples:
- Receive a buy notification if rsi is cold and bollinger is hot and aroon is cold.
- Receive a sell notification if 1d rsi is hot and 1h rsi is hot and bollinger is cold and aroon is hot.

**You will not receive notifications if all conditions, of one conditionnal, are not met.**

## Example

```yml
settings:
  log_level: INFO
  update_interval: 120
  start_worker_interval: 2
  market_data_chunk_size: 1
  timezone: Europe/Paris

exchanges:
  kraken:
    required:
      enabled: true
    all_pairs:
      - USD

indicators:
  rsi:
    - enabled: true
      alert_enabled: true
      alert_frequency: always
      signal:
        - rsi
      hot: 30
      cold: 70
      candle_period: 1h
      period_count: 14
    - enabled: true
      alert_enabled: true
      alert_frequency: always
      signal:
        - rsi
      hot: 40
      cold: 60
      candle_period: 1d
      period_count: 14
  bollinger:
    - enabled: true
      candle_period: 1h
      alert_enabled: true
      alert_frequency: always
      period_count: 25
      std_dev: 2.5
      signal:
        - low_band
        - close
        - up_band
      mute_cold: false
    - enabled: true
      candle_period: 1d
      alert_enabled: true
      alert_frequency: always
      period_count: 25
      std_dev: 2.5
      signal:
        - low_band
        - close
        - up_band
      mute_cold: false
  aroon_oscillator:
    - enabled: true
      alert_enabled: true
      alert_frequency: always
      sma_vol_period: 50
      period_count: 14
      signal:
        - aroon
      candle_period: 1h

conditionals:
  - label: "Signal to buy"
    hot:
      - rsi: 0
      - rsi: 1
    cold:
      - bollinger: 0
  - label: "Signal to buy"
    hot:
      - rsi: 1
  - label: "Signal to sell"
    cold:
      - rsi: 1
      - rsi: 0
    hot:
      - aroon_oscillator: 0

notifiers:
    telegram:
        required:
            token: X
            chat_id: Y
        optional:
            parse_mode: html
            template: "[{{market}}] {{indicator}} {{status}} {{values}} {{ '\n' -}}"
```

## Template value available
 - values
 - indicator
 - exchange
 - market
 - base_currency
 - quote_currency
 - status

 The `status` will be the string set in `label`.

# 9) Examples
Putting it all together an example config.yml might look like the config below if you want to use the default settings with bittrex

```yml
exchanges:
    bittrex:
        required:
            enabled: true
```

If you want to filter to a specific set of markets and receive updates hourly:

```yml
settings:
    update_interval: 300
    market_pairs:
        - ETH/BTC
        - DOGE/BTC

exchanges:
    bittrex:
        required:
            enabled: true
```

Now lets do something a little more involved and add the following to our above example:

- 21-period RSI over daily candlesticks
- 50-period RSI over hourly candlesticks
- 9-period hourly SMA

```yml
settings:
    update_interval: 300
    market_pairs:
        - ETH/BTC
        - DOGE/BTC

exchanges:
    bittrex:
        required:
            enabled: true

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
          period_count: 21
        - enabled: true
          alert_enabled: true
          alert_frequency: once
          signal:
            - rsi
          hot: 30
          cold: 70
          candle_period: 1h
          period_count: 50

informants:
    sma:
        - enabled: true
          signal:
            - sma
          candle_period: 1h
          period_count: 9
```

Another example:
- 2 exchanges
- 50-period RSI over hourly candlesticks
- 14-period RSI over 5minutes candlesticks
- 14-period Stoch-RSI over 5minutes candlesticks
- 14-period MFI over 5minutes candlesticks
- Momentum and MACD enabled, but without notifications
- obv, ichimoku not enabled
- 10-period EMA over daily candlesticks
- 30-period EMA over daily candlesticks
- EMA Crossover (crossing 10-period and 30-period)
- MACD Crossover (crossing macd and macdsignal)


Output template for notifications: " [5m / 15] huobipro - BTC/USDT - rsi - 1 is cold! ({'rsi': '80.19667083'}) "

```yml
settings:
    log_level: INFO
    update_interval: 500
    market_pairs:
        - BTC/USDT
        - ETH/USDT

exchanges:
    huobipro:
        required:
            enabled: true
    binance:
        required:
            enabled: true

indicators:
    rsi:
        - enabled: true
          alert_enabled: false
          alert_frequency: once
          signal:
            - rsi
          hot: 30
          cold: 70
          candle_period: 1h
          period_count: 50
        - enabled: true
          alert_enabled: true
          alert_frequency: once
          signal:
            - rsi
          hot: 30
          cold: 70
          candle_period: 5m
          period_count: 14
    stoch_rsi:
        - enabled: true
          alert_enabled: true
          alert_frequency: once
          signal:
            - stoch_rsi
          hot: 20
          cold: 80
          candle_period: 5m
          period_count: 14
    momentum:
        - enabled: true
          alert_enabled: false
          alert_frequency: once
          signal:
            - momentum
          hot: 0
          cold: 0
          candle_period: 1d
          period_count: 10
        - enabled: true
          alert_enabled: false
          alert_frequency: once
          signal:
            - momentum
          hot: 0
          cold: 0
          candle_period: 1h
          period_count: 12
    macd:
        - enabled: true
          alert_enabled: false
          alert_frequency: once
          signal:
            - macd
          hot: 0
          cold: 0
          candle_period: 15m
        - enabled: true
          alert_enabled: false
          alert_frequency: once
          signal:
            - macdsignal
          hot: 0
          cold: 0
          candle_period: 15m
    obv:
        - enabled: false
    mfi:
        - enabled: true
          alert_enabled: true
          alert_frequency: once
          signal:
            - mfi
          hot: 20
          cold: 80
          candle_period: 5m
          period_count: 14
    ichimoku:
        - enabled: false

informants:
    ema:
        - enabled: true
          signal:
            - ema
          candle_period: 1d
          period_count: 10
        - enabled: true
          signal:
            - ema
          candle_period: 1d
          period_count: 30

crossovers:
    std_crossover:
        - enabled: true
          alert_enabled: true
          alert_frequency: once
          key_indicator: ema
          key_indicator_index: 0
          key_indicator_type: informants
          key_signal: ema
          crossed_indicator: ema
          crossed_indicator_index: 1
          crossed_indicator_type: informants
          crossed_signal: ema
        - enabled: true
          alert_enabled: true
          alert_frequency: once
          key_indicator: macd
          key_indicator_index: 0
          key_indicator_type: indicators
          key_signal: macd
          crossed_indicator: macd
          crossed_indicator_index: 1
          crossed_indicator_type: indicators
          crossed_signal: macdsignal

notifiers:
    telegram:
        required:
            token: 4318021XXXX
            chat_id: -300XXXXXXX
        optional:
            parse_mode: html
            template: "[{{analysis.config.candle_period}} / {{analysis.config.period_count}}] {{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}! ({{values}}){{ '\n' -}}" 
```
