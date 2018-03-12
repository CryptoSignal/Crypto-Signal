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
description: This option controls how frequently to rescan the exchange information.

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

## Slack
*NOTIFIERS_SLACK_REQUIRED_WEBHOOK*\
default: None\
necessity: required for Slack\
description: The Slack webhook required for sending messages.

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

## Telegram
*NOTIFIERS_TELEGRAM_REQUIRED_TOKEN*\
default: None\
necessity: required for Telegram\
description: Your telegram bot token you can generate a token by following the instructions [here](https://core.telegram.org/bots#6-botfather)

*NOTIFIERS_TELEGRAM_REQUIRED_CHAT_ID*\
default: None\
necessity: required for Telegram\
description: The chat_id to send the message too. The easiest way to get get this id is probably using RawDataBot or Userinfobot.

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

# Analyzers
Settings for the analyzers behaviour. Valid indicators to set for hte below config options are currently
- MOMENTUM
- RSI
- MACD
- SMA
- EMA
- ICHIMOKU
- STOCHASTIC_RSI

*BEHAVIOUR_indicator_ENABLED*\
default: True\
necessity: optional\
description: Valid values are true or false. Whether to perform analysis on this indicator.

*BEHAVIOUR_indicator_ALERT_ENABLED*\
default: True\
necessity: optional\
description: Valid values are true or false. Whether to send alerts for this particular indicator.

*BEHAVIOUR_indicator_HOT*\
default:\
necessity: optional\
description: A valid option must be an integer or float. This is the number at which you want this indicator to become hot. For some indicators that is when it is above a threshold and for some it is below a threshold... this is automatically handled by the indicator you just need to provide the value.

*BEHAVIOUR_indicator_COLD*\
default:\
necessity: optional\
description: A valid option must be an integer or float. This is the number at which you want this indicator to become cold. For some indicators that is when it is above a threshold and for some it is below a threshold... this is automatically handled by the indicator you just need to provide the value.

*BEHAVIOUR_indicator_CANDLE_PERIOD*\
default: 1d\
necessity: optional\
description: Valid options vary by exchange, common options include 1m, 5m, 1h, 4h, 1d. This dictates what granularity of rollup to use for the analyzed candles, so a candle period of 1d will roll the candles up to 1 day blocks.

*BEHAVIOUR_indicator_PERIOD_COUNT*\
default:\
  SMA/EMA Crossovers: 15/21
  Other indicators: An integer
necessity: optional\
description: Valid options are an integer or list of integers separated by commas\*. This is the count of candle periods to use for this analysis. Let's suppose you wanted to test 15 days of EMA data. You would set the `BEHAVIOUR_EMA_CANDLE_PERIOD=1d` and then set `BEHAVIOUR_EMA_PERIOD_COUNT=15`, which means 15 counts of 1d periods... or in other words... 15 days. Furthermore, you can also keep track of the same indicator with multiple period lengths. If we wanted to watch the 15, 21, and 50 day EMA simultaneously, we could set `BEHAVIOUR_EMA_PERIOD_COUNT=15,21,50`.

\* When dealing with the SMA_CROSSOVER and EMA_CROSSOVER indicators, the PERIOD_COUNT setting takes two integers separated by a forward-slash. So if we wanted to know when the 15 SMA crosses over the 21 SMA, we could set `BEHAVIOUR_SMA_CROSSOVER_PERIOD_COUNT=15/21`.

# Exchanges
Settings that alter behaviour of interaction with an exchange.

*EXCHANGES_exchangeid_REQUIRED_ENABLED*\
default: False\
necessity: required\
description: Valid options are `true` or `false`. This setting enables or disables exchanges by specifying their id where specified in the variable name for bittrex the variable would be called `EXCHANGES_BITTREX_REQUIRED_ENABLED`. A list of exchange id's can be found [here](https://github.com/ccxt/ccxt/wiki/Exchange-Markets). In order to use crypto-signal you must set one exchange to true.

# Example
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
