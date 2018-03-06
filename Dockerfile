FROM python:3.6-jessie

# TA-lib is required by the python TA-lib wrapper. This provides analysis.
COPY lib/ta-lib-0.4.0-src.tar.gz /tmp/ta-lib-0.4.0-src.tar.gz

RUN cd /tmp && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

ADD app/ /app
WORKDIR /app

# numpy must be installed first for python TA-lib
RUN pip install numpy==1.14.0
RUN pip install -r requirements.txt

ENV SETTINGS_MARKET_PAIRS ETH/USD,LTC/USD,BTC/USD
ENV EXCHANGES_GDAX_REQUIRED_ENABLED false
ENV EXCHANGES_BITFINEX_REQUIRED_ENABLED true
ENV EXCHANGES_BITTREX_REQUIRED_ENABLED false
ENV SETTINGS_UPDATE_INTERVAL 30
ENV NOTIFIERS_SLACK_REQUIRED_WEBHOOK https://hooks.slack.com/services/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

ENV NOTIFIERS_DISCORD_REQUIRED_WEBHOOK https://discordapp.com/api/webhooks/420482355858374656/MW9Dq8UF_UiYZ-Qughjl58tGxmPlcQ1AODdItQfYydfqRPGj654o7fhpsNUw-5MczI7Z
ENV NOTIFIERS_DISCORD_REQUIRED_AVATAR https://pbs.twimg.com/profile_images/965010797452668928/7-Pfooe-_400x400.jpg
ENV NOTIFIERS_DISCORD_REQUIRED_USERNAME LamboRambo

CMD ["/usr/local/bin/python","app.py"]
