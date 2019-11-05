"""Handles sending notifications via the configured notifiers
"""

import json
import structlog
import os
import copy
import talib

import traceback

import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

from matplotlib.dates import DateFormatter
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from datetime import datetime
from pytz import timezone
from stockstats import StockDataFrame
from jinja2 import Template
from telegram.error import TimedOut as TelegramTimedOut

from notifiers.twilio_client import TwilioNotifier
from notifiers.slack_client import SlackNotifier
from notifiers.discord_client import DiscordNotifier
from notifiers.gmail_client import GmailNotifier
from notifiers.telegram_client import TelegramNotifier
from notifiers.webhook_client import WebhookNotifier
from notifiers.stdout_client import StdoutNotifier

from analyzers.utils import IndicatorUtils
from analyzers.indicators import ichimoku
from analyzers.indicators import candle_recognition

import sys

class Notifier(IndicatorUtils):
    """Handles sending notifications via the configured notifiers
    """

    def __init__(self, notifier_config, indicator_config, market_data):
        """Initializes Notifier class

        Args:
            notifier_config (dict): A dictionary containing configuration for the notifications.
        """

        self.logger = structlog.get_logger()
        self.notifier_config = notifier_config
        self.indicator_config = indicator_config
        self.market_data = market_data
        self.last_analysis = dict()
        self.enable_charts = False
        self.all_historical_data = False
        self.timezone = None
        self.first_run = False

        enabled_notifiers = list()
        self.logger = structlog.get_logger()
        self.twilio_configured = self._validate_required_config('twilio', notifier_config)
        if self.twilio_configured:
            self.twilio_client = TwilioNotifier(
                twilio_key=notifier_config['twilio']['required']['key'],
                twilio_secret=notifier_config['twilio']['required']['secret'],
                twilio_sender_number=notifier_config['twilio']['required']['sender_number'],
                twilio_receiver_number=notifier_config['twilio']['required']['receiver_number']
            )
            enabled_notifiers.append('twilio')

        self.discord_configured = self._validate_required_config('discord', notifier_config)
        if self.discord_configured:
            self.discord_client = DiscordNotifier(
                webhook=notifier_config['discord']['required']['webhook'],
                username=notifier_config['discord']['required']['username'],
                avatar=notifier_config['discord']['optional']['avatar']
            )
            enabled_notifiers.append('discord')

        self.slack_configured = self._validate_required_config('slack', notifier_config)
        if self.slack_configured:
            self.slack_client = SlackNotifier(
                slack_webhook=notifier_config['slack']['required']['webhook']
            )
            enabled_notifiers.append('slack')

        self.gmail_configured = self._validate_required_config('gmail', notifier_config)
        if self.gmail_configured:
            self.gmail_client = GmailNotifier(
                username=notifier_config['gmail']['required']['username'],
                password=notifier_config['gmail']['required']['password'],
                destination_addresses=notifier_config['gmail']['required']['destination_emails']
            )
            enabled_notifiers.append('gmail')

        self.telegram_configured = self._validate_required_config('telegram', notifier_config)
        if self.telegram_configured:
            self.telegram_client = TelegramNotifier(
                token=notifier_config['telegram']['required']['token'],
                chat_id=notifier_config['telegram']['required']['chat_id'],
                parse_mode=notifier_config['telegram']['optional']['parse_mode']
            )
            enabled_notifiers.append('telegram')

        self.webhook_configured = self._validate_required_config('webhook', notifier_config)
        if self.webhook_configured:
            self.webhook_client = WebhookNotifier(
                url=notifier_config['webhook']['required']['url'],
                username=notifier_config['webhook']['optional']['username'],
                password=notifier_config['webhook']['optional']['password']
            )
            enabled_notifiers.append('webhook')

        self.stdout_configured = self._validate_required_config('stdout', notifier_config)
        if self.stdout_configured:
            self.stdout_client = StdoutNotifier()
            enabled_notifiers.append('stdout')

        self.logger.info('enabled notifers: %s', enabled_notifiers)


    def notify_all(self, new_analysis):
        """Trigger a notification for all notification options.

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        charts_dir = './charts'

        messages = self.get_indicator_messages(new_analysis)

        if self.enable_charts == True:
            if not os.path.exists(charts_dir):
                os.mkdir(charts_dir)

            self.create_charts(messages)

        self.notify_slack(new_analysis)
        self.notify_discord(messages)
        self.notify_twilio(new_analysis)
        self.notify_gmail(new_analysis)
        self.notify_telegram(messages)
        self.notify_webhook(messages)
        self.notify_stdout(messages)

    def notify_discord(self, messages):
        """Send a notification via the discord notifier

        Args:
            messages (dict): The notification messages to send.
        """

        if not self.discord_configured:
            return

        message_template = Template(self.notifier_config['discord']['optional']['template'])

        for exchange in messages:
            for market_pair in messages[exchange]:
                _messages = messages[exchange][market_pair]
                                    
                for candle_period in _messages:
                    if not isinstance(_messages[candle_period], list) or len (_messages[candle_period]) == 0:
                        continue

                    self.notify_discord_message(_messages[candle_period], message_template)                 

    def notify_discord_message(self, messages, message_template):
        for message in messages:
            formatted_message = message_template.render(message)
            
            self.discord_client.notify(formatted_message.strip())


    def notify_slack(self, new_analysis):
        """Send a notification via the slack notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.slack_configured:
            message = self._indicator_message_templater(
                new_analysis,
                self.notifier_config['slack']['optional']['template']
            )
            if message.strip():
                self.slack_client.notify(message)


    def notify_twilio(self, new_analysis):
        """Send a notification via the twilio notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.twilio_configured:
            message = self._indicator_message_templater(
                new_analysis,
                self.notifier_config['twilio']['optional']['template']
            )
            if message.strip():
                self.twilio_client.notify(message)


    def notify_gmail(self, new_analysis):
        """Send a notification via the gmail notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.gmail_configured:
            message = self._indicator_message_templater(
                new_analysis,
                self.notifier_config['gmail']['optional']['template']
            )
            if message.strip():
                self.gmail_client.notify(message)


    def notify_telegram(self, messages):
        """Send notifications via the telegram notifier

        Args:
            messages (dict): The notification messages to send.
        """

        if not self.telegram_configured:
            return

        message_template = Template(self.notifier_config['telegram']['optional']['template'])

        for exchange in messages:
            for market_pair in messages[exchange]:
                _messages = messages[exchange][market_pair]
                                    
                for candle_period in _messages:
                    if not isinstance(_messages[candle_period], list) or len (_messages[candle_period]) == 0:
                        continue

                    if self.enable_charts == True:
                        self.notify_telegram_chart(exchange, market_pair, candle_period, _messages[candle_period], message_template)
                    else:
                        self.notify_telegram_message(_messages[candle_period], message_template)


    def notify_telegram_chart(self, exchange, market_pair, candle_period, messages, message_template):
        market_pair = market_pair.replace('/', '_').lower()
        chart_file = '{}/{}_{}_{}.png'.format('./charts', exchange, market_pair, candle_period)

        if os.path.exists(chart_file):
            try:
                self.telegram_client.send_chart(open(chart_file, 'rb'))
                self.notify_telegram_message(messages, message_template)
            except (IOError, SyntaxError) :
                self.notify_telegram_message(messages, message_template)
        else:
            self.logger.info('Chart file %s doesnt exist, sending text message.', chart_file)
            self.notify_telegram_message(messages, message_template)

    def notify_telegram_message(self, messages, message_template):
        try:
            for message in messages:
                formatted_message = message_template.render(message)
                self.telegram_client.notify(formatted_message.strip())
        except (TelegramTimedOut) as e:
            self.logger.info('Error TimeOut!')
            self.logger.info(e)

    def notify_webhook(self, messages):
        """Send notifications via a new webhook notifier

        Args:
            messages (dict): The notification messages to send.
        """

        if not self.webhook_configured:
            return

        for exchange in messages:
            for market_pair in messages[exchange]:
                _messages = messages[exchange][market_pair]
                                    
                for candle_period in _messages:
                    if not isinstance(_messages[candle_period], list) or len (_messages[candle_period]) == 0:
                        continue

                    self.webhook_client.notify(exchange, market_pair, candle_period, _messages[candle_period], self.enable_charts)          

    def notify_stdout(self, messages):
        """Send a notification via the stdout notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if not self.stdout_configured:
            return 

        message_template = Template(self.notifier_config['stdout']['optional']['template'])

        for exchange in messages:
            for market_pair in messages[exchange]:
                _messages = messages[exchange][market_pair]
                                    
                for candle_period in _messages:
                    if not isinstance(_messages[candle_period], list) or len (_messages[candle_period]) == 0:
                        continue

                    self.notify_stdout_message(_messages[candle_period], message_template)             

    def notify_stdout_message(self, messages, message_template):
        for message in messages:
            formatted_message = message_template.render(message)
            
            #self.discord_client.notify(formatted_message.strip())
            self.stdout_client.notify(formatted_message.strip())

    def _validate_required_config(self, notifier, notifier_config):
        """Validate the required configuration items are present for a notifier.

        Args:
            notifier (str): The name of the notifier key in default-config.json
            notifier_config (dict): A dictionary containing configuration for the notifications.

        Returns:
            bool: Is the notifier configured?
        """

        notifier_configured = True
        for _, val in notifier_config[notifier]['required'].items():
            if not val:
                notifier_configured = False
        return notifier_configured


    def _indicator_message_templater(self, new_analysis, template):
        """Creates a message from a user defined template

        Args:
            new_analysis (dict): A dictionary of data related to the analysis to send a message about.
            template (str): A Jinja formatted message template.

        Returns:
            str: The templated messages for the notifier.
        """

        if not self.last_analysis:
            self.last_analysis = new_analysis

        message_template = Template(template)
        new_message = str()
        for exchange in new_analysis:
            for market in new_analysis[exchange]:
                for indicator_type in new_analysis[exchange][market]:
                    if indicator_type == 'informants':
                        continue
                    for indicator in new_analysis[exchange][market][indicator_type]:
                        for index, analysis in enumerate(new_analysis[exchange][market][indicator_type][indicator]):
                            if analysis['result'].shape[0] == 0:
                                continue

                            values = dict()

                            if indicator_type == 'indicators':
                                for signal in analysis['config']['signal']:
                                    latest_result = analysis['result'].iloc[-1]

                                    values[signal] = analysis['result'].iloc[-1][signal]
                                    if isinstance(values[signal], float):
                                        values[signal] = format(values[signal], '.8f')
                            elif indicator_type == 'crossovers':
                                latest_result = analysis['result'].iloc[-1]

                                key_signal = '{}_{}'.format(
                                    analysis['config']['key_signal'],
                                    analysis['config']['key_indicator_index']
                                )

                                crossed_signal = '{}_{}'.format(
                                    analysis['config']['crossed_signal'],
                                    analysis['config']['crossed_indicator_index']
                                )

                                values[key_signal] = analysis['result'].iloc[-1][key_signal]
                                if isinstance(values[key_signal], float):
                                        values[key_signal] = format(values[key_signal], '.8f')

                                values[crossed_signal] = analysis['result'].iloc[-1][crossed_signal]
                                if isinstance(values[crossed_signal], float):
                                        values[crossed_signal] = format(values[crossed_signal], '.8f')

                            status = 'neutral'
                            if latest_result['is_hot']:
                                status = 'hot'
                            elif latest_result['is_cold']:
                                status = 'cold'

                            if 'indicator_label' in analysis['config']:
                                indicator_label = analysis['config']['indicator_label']
                            else:
                                indicator_label = '{} {}'.format(indicator, analysis['config']['candle_period'])

                            # Save status of indicator's new analysis
                            new_analysis[exchange][market][indicator_type][indicator][index]['status'] = status

                            if latest_result['is_hot'] or latest_result['is_cold']:

                                #Custom 'hot' or 'cold' labels
                                hot_cold_label = ''
                                if latest_result['is_hot'] and 'hot_label' in analysis['config']:
                                    hot_cold_label = analysis['config']['hot_label']
                                if latest_result['is_cold'] and 'cold_label' in analysis['config']:
                                    hot_cold_label = analysis['config']['cold_label']

                                try:
                                    last_status = self.last_analysis[exchange][market][indicator_type][indicator][index]['status']
                                except:
                                    last_status = str()

                                should_alert = True
                                if analysis['config']['alert_frequency'] == 'once':
                                    if last_status == status:
                                        should_alert = False

                                if not analysis['config']['alert_enabled']:
                                    should_alert = False

                                if should_alert:
                                    base_currency, quote_currency = market.split('/')
                                    new_message += message_template.render(
                                        values=values,
                                        exchange=exchange,
                                        market=market,
                                        base_currency=base_currency,
                                        quote_currency=quote_currency,
                                        indicator=indicator,
                                        indicator_number=index,
                                        analysis=analysis,
                                        status=status,
                                        last_status=last_status,
                                        hot_cold_label=hot_cold_label,
                                        indicator_label=indicator_label
                                    )

        # Merge changes from new analysis into last analysis
        self.last_analysis = {**self.last_analysis, **new_analysis}
        return new_message

    def get_indicator_messages(self, new_analysis):
        """Creates a message list from a user defined template

        Args:
            new_analysis (dict): A dictionary of data related to the analysis to send a message about.

        Returns:
            list: A list with the plain message data for the notifier.
        """

        if not self.last_analysis: #is the first run
            self.last_analysis = new_analysis
            self.first_run = True

        #self.logger.info('Is first run: {}'.format(self.first_run))

        now = datetime.now(timezone(self.timezone))
        creation_date = now.strftime("%Y-%m-%d %H:%M:%S")

        new_messages = dict()
        ohlcv_values = dict()
        lrsi_values = dict()

        for exchange in new_analysis:
            new_messages[exchange] = dict()
            ohlcv_values[exchange] = dict()
            lrsi_values[exchange] = dict()

            for market_pair in new_analysis[exchange]:

                new_messages[exchange][market_pair] = dict()
                ohlcv_values[exchange][market_pair] = dict()
                lrsi_values[exchange][market_pair] = dict()

                #Getting price values for each market pair and candle period
                for indicator_type in new_analysis[exchange][market_pair]:
                    if indicator_type == 'informants':
                        #Getting OHLC prices
                        for index, analysis in enumerate(new_analysis[exchange][market_pair]['informants']['ohlcv']):
                            values = dict()
                            for signal in analysis['config']['signal']:
                                values[signal] = analysis['result'].iloc[-1][signal]
                                ohlcv_values[exchange][market_pair][analysis['config']['candle_period']] = values

                        #Getting LRSI values
                        if 'lrsi' in new_analysis[exchange][market_pair]['informants']:
                            for index, analysis in enumerate(new_analysis[exchange][market_pair]['informants']['lrsi']):
                                values = dict()
                                for signal in analysis['config']['signal']:
                                    values[signal] = analysis['result'].iloc[-1][signal]
                            
                                lrsi_values[exchange][market_pair][analysis['config']['candle_period']] = values                                 

                for indicator_type in new_analysis[exchange][market_pair]:
                    if indicator_type == 'informants':
                        continue

                    for indicator in new_analysis[exchange][market_pair][indicator_type]:
                        for index, analysis in enumerate(new_analysis[exchange][market_pair][indicator_type][indicator]):
                            if analysis['result'].shape[0] == 0:
                                continue

                            values = dict()
                            if 'candle_period' in analysis['config']:
                                candle_period = analysis['config']['candle_period']

                                if not candle_period in new_messages[exchange][market_pair]:
                                    new_messages[exchange][market_pair][candle_period] = list()

                            if indicator_type == 'indicators':
                                for signal in analysis['config']['signal']:
                                    latest_result = analysis['result'].iloc[-1]

                                    values[signal] = analysis['result'].iloc[-1][signal]
                                    if isinstance(values[signal], float):
                                        values[signal] = format(values[signal], '.2f')
                            elif indicator_type == 'crossovers':
                                latest_result = analysis['result'].iloc[-1]

                                key_signal = '{}_{}'.format(
                                    analysis['config']['key_signal'],
                                    analysis['config']['key_indicator_index']
                                )

                                crossed_signal = '{}_{}'.format(
                                    analysis['config']['crossed_signal'],
                                    analysis['config']['crossed_indicator_index']
                                )

                                values[key_signal] = analysis['result'].iloc[-1][key_signal]
                                if isinstance(values[key_signal], float):
                                        values[key_signal] = format(values[key_signal], '.2f')

                                values[crossed_signal] = analysis['result'].iloc[-1][crossed_signal]
                                if isinstance(values[crossed_signal], float):
                                        values[crossed_signal] = format(values[crossed_signal], '.2f')

                            status = 'neutral'
                            if latest_result['is_hot']:
                                status = 'hot'
                            elif latest_result['is_cold']:
                                status = 'cold'

                            if 'indicator_label' in analysis['config']:
                                indicator_label = analysis['config']['indicator_label']
                            else:
                                indicator_label = ''

                            # Save status of indicator's new analysis
                            new_analysis[exchange][market_pair][indicator_type][indicator][index]['status'] = status

                            if latest_result['is_hot'] or latest_result['is_cold']:

                                #Custom 'hot' / 'cold' labels
                                hot_cold_label = ''
                                if latest_result['is_hot'] and 'hot_label' in analysis['config']:
                                    hot_cold_label = analysis['config']['hot_label']
                                if latest_result['is_cold'] and 'cold_label' in analysis['config']:
                                    hot_cold_label = analysis['config']['cold_label']

                                try:
                                    last_status = self.last_analysis[exchange][market_pair][indicator_type][indicator][index]['status']
                                except:
                                    last_status = str()

                                should_alert = True

                                #if self.first_run:
                                    #self.logger.info('Alert once for %s %s %s', market_pair, indicator, candle_period)
                                    
                                if not self.first_run:
                                    if analysis['config']['alert_frequency'] == 'once':
                                        if last_status == status:
                                            self.logger.info('Alert frecuency once. Dont alert. %s %s %s', 
                                            market_pair, indicator, candle_period)
                                            should_alert = False

                                if not analysis['config']['alert_enabled']:
                                    should_alert = False

                                if 'mute_cold' in analysis['config'] and latest_result['is_cold'] == analysis['config']['mute_cold']:
                                    self.logger.info('Skiping cold notification for %s %s %s', market_pair, indicator, candle_period)
                                    should_alert = False                                    

                                if should_alert:
                                    base_currency, quote_currency = market_pair.split('/')
                                    precision = self.market_data[exchange][market_pair]['precision']
                                    decimal_format = '.{}f'.format(precision['price'])

                                    prices = ''
                                    price_value = {}
                                    candle_period = analysis['config']['candle_period']
                                    candle_values = ohlcv_values[exchange][market_pair]

                                    if candle_period in candle_values :
                                        for key, value in candle_values[candle_period].items():
                                            price_value[key] = value

                                            value = format(value, decimal_format)
                                            prices = '{} {}: {}' . format(prices, key.title(), value)

                                    decimal_format = '%' + decimal_format

                                    lrsi = ''
                                    if candle_period in lrsi_values[exchange][market_pair]:
                                        lrsi = lrsi_values[exchange][market_pair][candle_period]['lrsi']
                                        lrsi = format(lrsi, '.2f')

                                    """
                                    new_message = message_template.render(
                                        values=values, exchange=exchange, market=market_pair, base_currency=base_currency,
                                        quote_currency=quote_currency, indicator=indicator, indicator_number=index,
                                        analysis=analysis, status=status, last_status=last_status, 
                                        prices=prices, lrsi=lrsi, creation_date=creation_date, indicator_label=indicator_label)
                                    """

                                    #save some memory removing unused data
                                    if 'result' in analysis:
                                        del analysis['result']

                                    new_message = dict(
                                        values=values, exchange=exchange, market=market_pair, base_currency=base_currency,
                                        quote_currency=quote_currency, indicator=indicator, indicator_number=index,
                                        analysis=analysis, status=status, last_status=last_status, 
                                        prices=prices, lrsi=lrsi, creation_date=creation_date, hot_cold_label=hot_cold_label,
                                        indicator_label=indicator_label, price_value = price_value, decimal_format=decimal_format)                                    

                                    new_messages[exchange][market_pair][candle_period].append(new_message)

        # Merge changes from new analysis into last analysis
        self.last_analysis = {**self.last_analysis, **new_analysis}

        if self.first_run == True:
            self.first_run = False

        return new_messages
    
    def set_timezone(self, timezone):
        self.timezone = timezone

    def set_enable_charts(self, enable_charts):
        self.enable_charts = enable_charts
    
    def set_all_historical_data(self, all_historical_data):
        self.all_historical_data = all_historical_data

    def create_charts(self, messages):
        """Create charts to be available for all notifiers

        Args:
            messages (dict): All notification messages grouped by exchange, market and candle period
        """

        for exchange in messages:
            for market_pair in messages[exchange]:
                _messages = messages[exchange][market_pair]
                                    
                for candle_period in _messages:
                    if len(_messages[candle_period]) == 0:
                        continue

                    candles_data = self.all_historical_data[exchange][market_pair][candle_period]

                    try:
                        self.create_chart(exchange, market_pair, candle_period, candles_data)
                    except Exception :
                        self.logger.info('Error creating chart for %s %s', market_pair, candle_period)

    def create_chart(self, exchange, market_pair, candle_period, candles_data):

        self.logger.info("Beginning creation of charts: {} - {} - {}".format(exchange, market_pair, candle_period))

        now = datetime.now(timezone(self.timezone))
        creation_date = now.strftime("%Y-%m-%d %H:%M:%S")

        df = self.convert_to_dataframe(candles_data)

        plt.rc('axes', grid=True)
        plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

        left, width = 0.1, 0.8
        rect1 = [left, 0.69, width, 0.23]
        rect2 = [left, 0.51, width, 0.18]
        rect3 = [left, 0.35, width, 0.16]
        rect4 = [left, 0.08, width, 0.23]

        fig = plt.figure(facecolor='white')
        fig.set_size_inches(8, 18, forward=True)
        axescolor = '#f6f6f6'  # the axes background color

        ax1 = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
        ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax1)
        ax3 = fig.add_axes(rect3, facecolor=axescolor, sharex=ax1)
        ax4 = fig.add_axes(rect4, facecolor=axescolor)

        # Plot Candles chart
        candle_pattern = self.candle_check(candles_data, candle_period)
        self.plot_candlestick(ax1, df, candle_period, candle_pattern)


        # Plot RSI (14)
        self.plot_rsi(ax2, df)

        # Calculate and plot MACD
        self.plot_macd(ax3, df, candle_period)

        # Plot ichimoku
        self.plot_ichimoku(ax4, df, candles_data, candle_period)

        for ax in ax1, ax2, ax3, ax4:
            if ax != ax3 and ax != ax4:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
            elif ax == ax3:
                for label in ax.get_xticklabels():
                    label.set_rotation(30)
                    label.set_horizontalalignment('right')
            elif ax == ax4:
                for label in ax.get_xticklabels():
                    label.set_rotation(30)
                    label.set_horizontalalignment('right')

            ax.xaxis.set_major_locator(mticker.MaxNLocator(10))
            ax.xaxis.set_major_formatter(DateFormatter('%d/%b'))
            ax.xaxis.set_tick_params(which='major', pad=15)

        fig.autofmt_xdate()

        title = '{} {} {} - {}'.format(exchange, market_pair, candle_period, creation_date).upper()
        fig.suptitle(title, fontsize=14)

        market_pair = market_pair.replace('/', '_').lower()
        chart_file = '{}/{}_{}_{}.png'.format('./charts', exchange, market_pair, candle_period)

        plt.savefig(chart_file)
        plt.close(fig)

        return chart_file

    def candlestick_ohlc(self, ax, quotes, cdl=None, width=0.2, colorup='k', colordown='r',
                    alpha=1.0, ochl=False):
        """
        Plot the time, open, high, low, close as a vertical line ranging
        from low to high.  Use a rectangular bar to represent the
        open-close span.  If close >= open, use colorup to color the bar,
        otherwise use colordown

        Parameters
        ----------
        ax : `Axes`
            an Axes instance to plot to
        quotes : sequence of quote sequences
            data to plot.  time must be in float date format - see date2num
            (time, open, high, low, close, ...) vs
            (time, open, close, high, low, ...)
            set by `ochl`
        cdl : candle pattern recognition from analysis if enabled
        width : float
            fraction of a day for the rectangle width
        colorup : color
            the color of the rectangle where close >= open
        colordown : color
            the color of the rectangle where close <  open
        alpha : float
            the rectangle alpha level
        ochl: bool
            argument to select between ochl and ohlc ordering of quotes

        Returns
        -------
        ret : tuple
            returns (lines, patches) where lines is a list of lines
            added and patches is a list of the rectangle patches added

        """

        if isinstance(cdl, pd.DataFrame):
            if pd.DataFrame(cdl).empty:
                cdl_pattern = False
            else:
                cdl_pattern = True
        else:
            cdl_pattern = False

        OFFSET = width / 2.0
        # colors used for candle patterns
        colors = ['c', 'm', 'y', 'k', 'b']
        index = 0
        lines = []
        patches = []

        for q in quotes:
            if ochl:
                t, open, close, high, low = q[:5]
            else:
                t, open, high, low, close = q[:5]
            if close >= open:
                if cdl_pattern:
                    for column in cdl:
                        if cdl[column][index]!= 0:
                            color = colors[cdl.columns.get_loc(column)]
                            break
                        else:
                            color = colorup
                else:
                    color = colorup
                lower = open
                height = close - open
            else:
                if cdl_pattern:
                    for column in cdl:
                        if cdl[column][index] != 0:
                            color = colors[cdl.columns.get_loc(column)]
                            break
                        else:
                            color = colordown
                else:
                    color = colordown
                lower = close
                height = open - close

            vline = Line2D(
                xdata=(t, t), ydata=(low, high),
                color=color,
                linewidth=0.5,
                antialiased=False,
            )

            rect = Rectangle(
                xy=(t - OFFSET, lower),
                width=width,
                height=height,
                facecolor=color,
                edgecolor=None,
                antialiased=False,
                alpha=1.0
            )

            lines.append(vline)
            patches.append(rect)
            ax.add_line(vline)
            ax.add_patch(rect)

            index += 1

        ax.autoscale_view()

        return lines, patches

    def candle_check(self, df, candle_period):
        """
        df : dataframe with ohlcv values
        candle_period : period for candles
        return : dataframe with candle patterns
        """
        try:
            indicator_conf = {}

            if 'candle_recognition' in self.indicator_config:
                for config in self.indicator_config['candle_recognition']:
                    if config['enabled'] and config['candle_period'] == candle_period and config['chart']:
                        indicator_conf = config
                        break

            if bool(indicator_conf):
                signal = indicator_conf['signal']
                notification = indicator_conf['notification'] if 'notification' in indicator_conf else 'hot'
                candle_check = indicator_conf['candle_check'] if 'candle_check' in indicator_conf else 1
                hot_tresh = indicator_conf['hot']
                cold_tresh = indicator_conf['cold']

                historical_data = df
                cdl = candle_recognition.Candle_recognition()
                candle_pattern = cdl.analyze(historical_data, signal, notification, candle_check, hot_tresh, cold_tresh)
                candle_pattern = candle_pattern.drop(['is_hot', 'is_cold'], axis=1)
            else:
                candle_pattern = pd.DataFrame()

        except Exception:
            self.logger.info('error in indicator config for candle pattern: {}'.format(sys.exc_info()[0]))

        return candle_pattern

    def plot_candlestick(self, ax, df, candle_period, candle_pattern):
        textsize = 11

        ma7  = self.EMA(df, 7)
        ma25 = self.EMA(df, 25)
        ma99 = self.EMA(df, 99)


        if(df['close'].count() > 120):
            df   = df.iloc[-120:]
            ma7  = ma7.iloc[-120:]
            ma25 = ma25.iloc[-120:]
            ma99 = ma99.iloc[-120:]
            candle_pattern = candle_pattern.iloc[-120:]

        _time = mdates.date2num(df.index.to_pydatetime())
        min_x = np.nanmin(_time)
        max_x = np.nanmax(_time)

        stick_width = ((max_x - min_x) / _time.size )             

        ax.set_ymargin(0.2)
        ax.ticklabel_format(axis='y', style='plain')

        try:
            self.candlestick_ohlc(ax, zip(_time, df['open'], df['high'], df['low'], df['close']), cdl=candle_pattern,
                    width=stick_width, colorup='olivedrab', colordown='crimson')
        except:
            print(traceback.print_exc())

        ax.plot(df.index, ma7, color='darkorange', lw=0.8, label='EMA (7)')
        ax.plot(df.index, ma25, color='mediumslateblue', lw=0.8, label='EMA (25)')
        ax.plot(df.index, ma99, color='firebrick', lw=0.8, label='EMA (99)')

        ax.text(0.04, 0.94, 'EMA (7, close)', color='darkorange', transform=ax.transAxes, fontsize=textsize, va='top')
        ax.text(0.24, 0.94, 'EMA (25, close)', color='mediumslateblue', transform=ax.transAxes,  fontsize=textsize, va='top')
        ax.text(0.46, 0.94, 'EMA (99, close)', color='firebrick', transform=ax.transAxes,  fontsize=textsize, va='top')

    def plot_rsi(self, ax, df):
        textsize = 11
        fillcolor = 'darkmagenta'

        rsi = self.relative_strength(df["close"])

        if(df['close'].count() > 120):
            df = df.iloc[-120:]
            rsi = rsi[-120:]     

        ax.plot(df.index, rsi, color=fillcolor, linewidth=0.5)
        ax.axhline(70, color='darkmagenta', linestyle='dashed', alpha=0.6)
        ax.axhline(30, color='darkmagenta', linestyle='dashed', alpha=0.6)
        ax.fill_between(df.index, rsi, 70, where=(rsi >= 70),
                        facecolor=fillcolor, edgecolor=fillcolor)
        ax.fill_between(df.index, rsi, 30, where=(rsi <= 30),
                        facecolor=fillcolor, edgecolor=fillcolor)
        ax.set_ylim(0, 100)
        ax.set_yticks([30, 70])
        ax.text(0.024, 0.94, 'RSI (14)', va='top',transform=ax.transAxes, fontsize=textsize)

    def plot_macd(self, ax, df, candle_period):
        textsize = 11

        df = StockDataFrame.retype(df)
        df['macd'] = df.get('macd')

        if(df['macd'].count() > 120):
            df = df.iloc[-120:]

        min_y = df.macd.min()
        max_y = df.macd.max()

        #Reduce Macd Histogram values to have a better visualization
        macd_h = df.macdh * 0.5

        if (macd_h.min() < min_y):
            min_y = macd_h.min()

        if (macd_h.max() > max_y):
            max_y = macd_h.max() 

        #Adding some extra space at bottom/top
        min_y = min_y * 1.2
        max_y = max_y * 1.2

        #Define candle bar width
        _time = mdates.date2num(df.index.to_pydatetime())
        min_x = np.nanmin(_time)
        max_x = np.nanmax(_time)

        bar_width = ((max_x - min_x) / _time.size ) * 0.8            

        ax.bar(x=_time, bottom=[0 for _ in macd_h.index], height=macd_h, width=bar_width, color="red", alpha = 0.4)
        ax.plot(_time, df.macd, color='blue', lw=0.6)
        ax.plot(_time, df.macds, color='red', lw=0.6)
        ax.set_ylim((min_y, max_y))
    
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))
        ax.text(0.024, 0.94, 'MACD (12, 26, close, 9)', va='top', transform=ax.transAxes, fontsize=textsize) 

    def plot_ppsr(self, ax, df, candle_period):
        """Calculate Pivot Points, Supports and Resistances for given data
        
        :param df: pandas.DataFrame
        :return: pandas.DataFrame
        """
        PP = pd.Series((df['high'] + df['how'] + df['close']) / 3)
        R1 = pd.Series(2 * PP - df['low'])
        S1 = pd.Series(2 * PP - df['high'])
        R2 = pd.Series(PP + df['high'] - df['low'])
        S2 = pd.Series(PP - df['high'] + df['low'])
        R3 = pd.Series(df['high'] + 2 * (PP - df['low']))
        S3 = pd.Series(df['low'] - 2 * (df['high'] - PP))
        psr = {'PP': PP, 'R1': R1, 'S1': S1, 'R2': R2, 'S2': S2, 'R3': R3, 'S3': S3}
        PSR = pd.DataFrame(psr)
        df = df.join(PSR)
        return df

    def relative_strength(self, prices, n=14):
        """
        compute the n period relative strength indicator
        http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
        http://www.investopedia.com/terms/r/rsi.asp
        """

        deltas = np.diff(prices)
        seed = deltas[:n + 1]
        up = seed[seed >= 0].sum() / n
        down = -seed[seed < 0].sum() / n
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100. / (1. + rs)

        for i in range(n, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (n - 1) + upval) / n
            down = (down * (n - 1) + downval) / n

            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

        return rsi


    def moving_average(self, x, n, type='simple'):
        """
        compute an n period moving average.

        type is 'simple' | 'exponential'

        """
        x = np.asarray(x)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))

        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a


    def EMA(self, df, n, field = 'close'):
        return pd.Series(talib.EMA(df[field].astype('f8').values, n), name = 'EMA_' + field.upper() + '_' + str(n), index = df.index)        


    def plot_ichimoku(self, ax, df, historical_data, candle_period):
        indicator_conf = {}

        if 'ichimoku' in self.indicator_config:
            for config in self.indicator_config['ichimoku']:
                if config['enabled'] and config['candle_period'] == candle_period:
                    indicator_conf = config
                    break

        tenkansen_period = indicator_conf['tenkansen_period'] if 'tenkansen_period' in indicator_conf else 20                       
        kijunsen_period = indicator_conf['kijunsen_period'] if 'kijunsen_period' in indicator_conf else 60
        senkou_span_b_period = indicator_conf['senkou_span_b_period'] if 'senkou_span_b_period' in indicator_conf else 120
        
        textsize = 11
        ichimoku_data = ichimoku.Ichimoku().analyze(historical_data, tenkansen_period, kijunsen_period , senkou_span_b_period, chart=True)

        if(df['close'].count() > 120):
            df = df.iloc[-120:]
            ##change 146 if cloud displacement period changed in ichimoku.Ichimoku().calculate()##
            ichimoku_data = ichimoku_data.iloc[-146:]

        _time = mdates.date2num(df.index.to_pydatetime())
        _time2 = mdates.date2num(ichimoku_data.index.to_pydatetime())

        min_x = np.nanmin(_time)
        max_x = np.nanmax(_time)

        stick_width = ((max_x - min_x) / _time.size )

        ax.set_ymargin(0.2)
        ax.ticklabel_format(axis='y', style='plain')

        self.candlestick_ohlc(ax, zip(_time, df['open'], df['high'], df['low'], df['close']),
                    width=stick_width, colorup='olivedrab', colordown='crimson')

        kijunsen = ichimoku_data.kijunsen
        tenkansen = ichimoku_data.tenkansen
        leading_span_a = ichimoku_data.leading_span_a
        leading_span_b = ichimoku_data.leading_span_b
        ax.plot(_time2, kijunsen, color='red', lw=0.6)
        ax.plot(_time2, tenkansen, color='blue', lw=0.6)
        ax.plot(_time2, leading_span_a, color='darkgreen', lw=0.6, linestyle='dashed')
        ax.plot(_time2, leading_span_b, color='darkred', lw=0.6, linestyle='dashed')

        ax.fill_between(_time2, leading_span_a, leading_span_b, where = leading_span_a > leading_span_b,
                        facecolor='#008000', interpolate=True, alpha=0.25)
        ax.fill_between(_time2, leading_span_a, leading_span_b, where=leading_span_b > leading_span_a,
                        facecolor='#ff0000', interpolate=True, alpha=0.25)

        ax.text(0.04, 0.94, 'kijunsen', color='red', transform=ax.transAxes, fontsize=textsize, va='top')
        ax.text(0.20, 0.94, 'tenkansen', color='blue', transform=ax.transAxes, fontsize=textsize, va='top')
        ax.text(0.44, 0.94, '-Senkou-Span-A-', color='darkgreen', transform=ax.transAxes, fontsize=textsize, va='top', fontstyle='italic')
        ax.text(0.66, 0.94, '-Senkou-Span-B-', color='darkred', transform=ax.transAxes, fontsize=textsize, va='top', fontstyle='italic')
