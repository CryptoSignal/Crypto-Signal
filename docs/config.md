# Settings
General settings for crypto-signal

*SETTINGS_LOG_MODE*\
default: text\
necessity: optional\
description: Can be set to `text`, `json` or `standard`. This will specify the log format for events emitted by the logger.

*SETTINGS_LOG_LEVEL*\
default: INFO\
necessity: optional\
description: Can be set to `DEBUG`, `INFO`, `WARN`, `ERROR`. Used to set the logger verbosity.

*SETTINGS_OUTPUT_MODE*\
default: cli\
necessity: optional\
description: Can be set to `cli`, `csv` or `json`. This will specify the output format for events emitted by the app.

*SETTINGS_UPDATE_INTERVAL*\
default: 300\
necessity: optional\
description: This option controls how frequently to rescan the exchange information (in seconds).

*SETTINGS_MARKET_PAIRS*\
default: None\
necessity: optional\
description: Allows you to specify a comma separated list of market pairs you are interested in. For example `ETH/BTC,DOGE/BTC`.

# Notifiers
Settings to configure where to notify when a hot or cold threshold is tripped.

## Twilio
*NOTIFIERS_TWILIO_REQUIRED_KEY*\
default: None\
necessity: required for Twilio\
description: The twilio API key required for communication.

*NOTIFIERS_TWILIO_REQUIRED_SECRET*\
default: None\
necessity: required for Twilio\
description: The twilio API key secret required for communication.

*NOTIFIERS_TWILIO_REQUIRED_SENDER_NUMBER*\
default: None\
necessity: required for Twilio\
description: The twilio phone number for sending the message.

*NOTIFIERS_TWILIO_REQUIRED_RECEIVER_NUMBER*\
default: None\
necessity: required for Twilio\
description: The receiving phone number (your phone number) for receiving the message.

*NOTIFIERS_TWILIO_OPTIONAL_TEMPLATE*\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

## Slack
*NOTIFIERS_SLACK_REQUIRED_WEBHOOK*\
default: None\
necessity: required for Slack\
description: The Slack webhook required for sending messages.

*NOTIFIERS_SLACK_OPTIONAL_TEMPLATE*\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

## Gmail
*NOTIFIERS_GMAIL_REQUIRED_USERNAME*\
default: None\
necessity: required for Gmail\
description: Your gmail username which is required for sending emails.

*NOTIFIERS_GMAIL_REQUIRED_PASSWORD*\
default: None\
necessity: required for Gmail\
description: Your gmail password which is required for sending emails.

*NOTIFIERS_GMAIL_REQUIRED_DESTINATION_EMAILS*\
default: None\
necessity: required for Gmail\
description: The email addresses to receive the emails that are sent.

*NOTIFIERS_GMAIL_OPTIONAL_TEMPLATE*\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

## Telegram
*NOTIFIERS_TELEGRAM_REQUIRED_TOKEN*\
default: None\
necessity: required for Telegram\
description: Your telegram bot token you can generate a token by following the instructions [here](https://core.telegram.org/bots#6-botfather)

*NOTIFIERS_TELEGRAM_REQUIRED_CHAT_ID*\
default: None\
necessity: required for Telegram\
description: The chat_id to send the message too. The easiest way to get get this id is probably using RawDataBot or Userinfobot.

*NOTIFIERS_TELEGRAM_OPTIONAL_TEMPLATE*\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

## Discord
*NOTIFIERS_DISCORD_REQUIRED_WEBHOOK*\
default: None\
necessity: required for Discord\
description: The Discord webhook REQUIRED for sending messages.

*NOTIFIERS_DISCORD_REQUIRED_USERNAME*\
default: None\
necessity: required for Discord\
description: The Discord username that will be sending messages. Can be anything.

*NOTIFIERS_DISCORD_OPTIONAL_AVATAR*\
default: None\
necessity: optional for Discord\
description: The Discord avatar image for the username sending messages. Set to None for default pokemon.

*NOTIFIERS_DISCORD_OPTIONAL_TEMPLATE*\
default: {{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}\
necessity: optional\
description: See the notifier templating section.

# Notifier Templating
The notifier templates are built with a templating language called [Jinja2](http://jinja.pocoo.org/docs/2.10/templates/) and anything that is a valid Jinja message is valid for crypto-signal. The options available are as follows:

- exchange - The name of the exchange for the indicator.
- market - The name of the market for the indicator.
- indicator - The name of the analyzer used for this indicator.
- indicator_number - Which configured instance of the analyzer this indicator applies too.
- status - Whether the indicator is hot, cold or neutral.
- last_status - The status of the previous analysis run.
- values.<signal_line> - The stringified value from the selected signal line, see the indicator section for the signal lines available for each indicator.
- analysis.result.<signal_line> - The raw value from the selected signal line, see the indicator section for the signal lines available for each indicator.
- analysis.result.is_hot - The raw boolean value of if the indicator is hot.
- analysis.result.is_cold - The raw boolean value of if the indicator is cold.
- analysis.config.enabled - The raw config item of if this indicator is enabled. If you receive a message with a value other than True something has gone horribly wrong.
- analysis.config.alert_enabled - The raw config item of if this indicator alert is enabled. If you receive a message with a value other than True something has gone horribly wrong.
- analysis.config.alert_frequency - The raw config item of whether this alert is always sent or if it is only sent once per status change.
- analysis.config.hot - The raw config item of what the configured hot threshold is.
- analysis.config.cold - The raw config item of what the configured cold threshold is.
- analysis.config.candle_period - The raw config item of what time period of candles to gather.
- analysis.config.period_count - The raw config item of how many candles to gather.
- analysis.config.signal_line - The raw config item of the configured signal lines.

As an example of how to use it, lets say you want to write a custom message for discord... it would end up looking something like...

```
NOTIFIERS_DISCORD_OPTIONAL_TEMPLATE="[{{analysis.config.candle_period}}] {{market}} on {{exchange}} is {{status}}"
```

The result of the above custom template would generate a message that looks like: [1h] BURST/BTC on bittrex is hot.

# Analyzers
Settings for the analyzers behaviour.

## Valid settings for indicators

The formal grammar is defined as follows:

```
<indicator> := <indicator_name>_<indicator_index>

<indicator_name> := MOMENTUM |
                    RSI |
                    MACD |
                    ICHIMOKU |
                    STOCHASTIC_RSI |
                    MFI |
                    OBV

<indicator_index> := {0, 1, 2, ...}
```

Every indicator has a default set of signal lines, you can also tweak them to your liking. The first signal that you specify in the list is the signal tested for hot/cold and the others are output to the console.

```
MOMENTUM - momentum
RSI - rsi
MACD - macd
ICHIMOKU - leading_span_a, leading_span_b
STOCHASTIC_RSI - stoch_rsi
MFI - mfi
OBV - obv
```

*INDICATOR_\<indicator_name\>_NUM_INDICATORS*\
default: 1\
necessity: optional\
description: Valid values are positive integers. This tells Crypto-Signal how many of the same indicator to keep track of.

*INDICATOR_\<indicator\>_ENABLED*\
default: True\
necessity: optional\
description: Valid values are true or false. Whether to perform analysis on this indicator.

*INDICATOR_\<indicator\>_ALERT_ENABLED*\
default: True\
necessity: optional\
description: Valid values are true or false. Whether to send alerts for this particular indicator.

*INDICATOR_\<indicator\>_SIGNAL_LINE*\
default: A string\
necessity: optional\
description: Valid values are on a per indicator basis see the options in the table at the start of the analyzers section for a full list of what is available. Each indicator may have a variety of signal lines, this option allows you to specify which options you care about. The first one specified is used for determining hot/cold the others are just output to the cli for information.

*INDICATOR_\<indicator\>_HOT*\
default:\
necessity: optional\
description: A valid option must be an integer or float. This is the number at which you want this indicator to become hot. For some indicators that is when it is above a threshold and for some it is below a threshold... this is automatically handled by the indicator you just need to provide the value.

*INDICATOR_\<indicator\>_COLD*\
default:\
necessity: optional\
description: A valid option must be an integer or float. This is the number at which you want this indicator to become cold. For some indicators that is when it is above a threshold and for some it is below a threshold... this is automatically handled by the indicator you just need to provide the value.

*INDICATOR_\<indicator\>_CANDLE_PERIOD*\
default: 1d\
necessity: optional\
description: Valid options vary by exchange, common options include 1m, 5m, 1h, 4h, 1d. This dictates what granularity of rollup to use for the analyzed candles, so a candle period of 1d will roll the candles up to 1 day blocks.

*INDICATOR_\<indicator\>_PERIOD_COUNT*\
default: An integer\
necessity: optional\
description: Valid options are an integer. This is the count of candle periods to use for this analysis. Let's suppose you wanted to test 15 days of RSI data. You would set the `INDICATOR_RSI_0_CANDLE_PERIOD=1d` and then set `INDICATOR_RSI_0_PERIOD_COUNT=15`, which means 15 counts of 1d periods... or in other words... 15 days. Furthermore, you can also keep track of the same indicator with multiple period lengths. If we wanted to watch the 15, 21, and 50 day RSI simultaneously, we could set `INDICATOR_RSI_0_PERIOD_COUNT=15`, `INDICATOR_RSI_1_PERIOD_COUNT=21`, `INDICATOR_RSI_2_PERIOD_COUNT=50`.

## Valid settings for informants

The formal grammar is defined as follows:

```
<indicator> := <indicator_name>_<indicator_index>

<indicator_name> := SMA |
                    EMA |
                    VWAP |
                    BOL_BAND

<indicator_index> := {0, 1, 2, ...}
```

Every indicator has a default set of signal lines, you can also tweak them to your liking. If you specify the signal lines it determines which ones are output to the console.

```
SMA - sma
EMA - ema
VWAP - vwap
BOL_BAND - upperband, middleband, lowerband
```

*INFORMANT_\<indicator_name\>_NUM_INDICATORS*\
default: 1\
necessity: optional\
description: Valid values are positive integers. This tells Crypto-Signal how many of the same indicator to keep track of.

*INFORMANT_\<indicator\>_ENABLED*\
default: True\
necessity: optional\
description: Valid values are true or false. Whether to perform analysis on this indicator.

*INFORMANT_\<indicator\>_SIGNAL_LINE*\
default: A string\
necessity: optional\
description: Valid values are on a per indicator basis see the options in the table at the start of the analyzers section for a full list of what is available. Each indicator may have a variety of signal lines, this option allows you to specify which options you care about.

*INFORMANT_\<indicator\>_PERIOD_COUNT*\
default: An integer\
necessity: optional\
description: Valid options are an integer. This is the count of candle periods to use for this analysis. Let's suppose you wanted to test 15 days of EMA data. You would set the `INFORMANT_EMA_0_CANDLE_PERIOD=1d` and then set `INFORMANT_EMA_0_PERIOD_COUNT=15`, which means 15 counts of 1d periods... or in other words... 15 days. Furthermore, you can also keep track of the same indicator with multiple period lengths. If we wanted to watch the 15, 21, and 50 day EMA simultaneously, we could set `INFORMANT_EMA_0_PERIOD_COUNT=15`, `INFORMANT_EMA_1_PERIOD_COUNT=21`, `INFORMANT_EMA_2_PERIOD_COUNT=50`.

## Valid settings for crossovers

The formal grammar is defined as follows:

```
<indicator> := <indicator_name>_<indicator_index>

<indicator_name> := STD_CROSSOVER

<indicator_index> := {0, 1, 2, ...}
```

*CROSSOVER_\<indicator_name\>_NUM_INDICATORS*\
default: 1\
necessity: optional\
description: Valid values are positive integers. This tells Crypto-Signal how many of the same indicator to keep track of.

*CROSSOVER_\<indicator\>_ENABLED*\
default: False\
necessity: optional\
description: Valid values are true or false. Whether to perform analysis on this indicator.

*CROSSOVER_\<indicator\>_ALERT_ENABLED*\
default: False\
necessity: optional\
description: Valid values are true or false. Whether to send alerts for this particular indicator.

*CROSSOVER_\<indicator\>_KEY_INDICATOR*\
default: N/A\
necessity: optional\
description: Valid values are the name of any indicator or informant. The indicator that gets hot when it goes above the crossed indicator and cold when it goes below it.

*CROSSOVER_\<indicator\>_KEY_INDICATOR_INDEX*\
default: N/A\
necessity: optional\
description: Valid values are positive integers. The index of the selected key indicator or informant that you want to use.

*CROSSOVER_\<indicator\>_KEY_INDICATOR_TYPE*\
default: N/A\
necessity: optional\
description: Valid values are 'indicator' or 'informant'. Whether the key indicator is of type informant or indicator.

*CROSSOVER_\<indicator\>_KEY_SIGNAL*\
default: N/A\
necessity: optional\
description: Valid values are the name of a signal line for the select indicator or informant. Which signal to use of the selected indicator or informant.

*CROSSOVER_\<indicator\>_CROSSED_INDICATOR*\
default: N/A\
necessity: optional\
description: Valid values are the name of any indicator or informant. The indicator or informant that the key indicator is intended to cross.

*CROSSOVER_\<indicator\>_CROSSED_INDICATOR_INDEX*\
default: N/A\
necessity: optional\
description: Valid values are positive integers. The index of the selected crossed indicator or informant that you want to use.

*CROSSOVER_\<indicator\>_CROSSED_INDICATOR_TYPE*\
default: N/A\
necessity: optional\
description: Valid values are 'indicator' or 'informant'. Whether the crossed indicator is of type informant or indicator.

*CROSSOVER_\<indicator\>_CROSSED_SIGNAL*\
default: N/A\
necessity: optional\
description: Valid values are the name of a signal line for the select indicator or informant. Which signal to use of the selected indicator or informant.

# Exchanges
Settings that alter behaviour of interaction with an exchange.

*EXCHANGES_exchangeid_REQUIRED_ENABLED*\
default: False\
necessity: required\
description: Valid options are `true` or `false`. This setting enables or disables exchanges by specifying their id where specified in the variable name for bittrex the variable would be called `EXCHANGES_BITTREX_REQUIRED_ENABLED`. A list of exchange id's can be found [here](https://github.com/ccxt/ccxt/wiki/Exchange-Markets). In order to use crypto-signal you must set one exchange to true.

# Examples
Putting it all together an example settings.env might look like the config below if you want to use the default settings with bittrex

```
EXCHANGES_BITTREX_REQUIRED_ENABLED=true
```

If you want to filter to a specific set of markets and receive updates hourly:

```
SETTINGS_MARKET_PAIRS=ETH/BTC,DOGE/BTC
SETTINGS_UPDATE_INTERVAL=3600
EXCHANGES_BITTREX_REQUIRED_ENABLED=true
```

To hammer home this unique (and perhaps arcane) method of configuration, consider how we can translate the following example into a proper configuration using the grammar above:

- 21-period RSI over daily candlesticks
- 50-period RSI over hourly candlesticks
- 9-period hourly SMA

This is the respective configuration for settings.env:

```
INDICATOR_RSI_NUM_INDICATORS=2
INDICATOR_RSI_0_CANDLE_PERIOD=1d
INDICATOR_RSI_0_PERIOD_COUNT=21
INDICATOR_RSI_1_CANDLE_PERIOD=1h
INDICATOR_RSI_1_PERIOD_COUNT=50
INDICATOR_SMA_0_PERIOD_COUNT=9
INDICATOR_SMA_0_CANDLE_PERIOD=1h
```

Notice that we don't need to specify the _NUM_INDICATORS_ option if we are only using a single instance of an indicator.
