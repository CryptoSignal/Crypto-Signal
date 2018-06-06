"""Handles sending notifications via the configured notifiers
"""

import json
import structlog
from jinja2 import Template

from notifiers.twilio_client import TwilioNotifier
from notifiers.slack_client import SlackNotifier
from notifiers.discord_client import DiscordNotifier
from notifiers.gmail_client import GmailNotifier
from notifiers.telegram_client import TelegramNotifier
from notifiers.webhook_client import WebhookNotifier
from notifiers.stdout_client import StdoutNotifier

class Notifier():
    """Handles sending notifications via the configured notifiers
    """

    def __init__(self, notifier_config):
        """Initializes Notifier class

        Args:
            notifier_config (dict): A dictionary containing configuration for the notifications.
        """

        self.logger = structlog.get_logger()
        self.notifier_config = notifier_config
        self.last_analysis = dict()

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

        self.notify_slack(new_analysis)
        self.notify_discord(new_analysis)
        self.notify_twilio(new_analysis)
        self.notify_gmail(new_analysis)
        self.notify_telegram(new_analysis)
        self.notify_webhook(new_analysis)
        self.notify_stdout(new_analysis)

    def notify_discord(self, new_analysis):
        """Send a notification via the discord notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.discord_configured:
            message = self._indicator_message_templater(
                new_analysis,
                self.notifier_config['discord']['optional']['template']
            )
            if message.strip():
                self.discord_client.notify(message)


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


    def notify_telegram(self, new_analysis):
        """Send a notification via the telegram notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.telegram_configured:
            message = self._indicator_message_templater(
                new_analysis,
                self.notifier_config['telegram']['optional']['template']
            )
            if message.strip():
                self.telegram_client.notify(message)


    def notify_webhook(self, new_analysis):
        """Send a notification via the webhook notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.webhook_configured:
            for exchange in new_analysis:
                for market in new_analysis[exchange]:
                    for indicator_type in new_analysis[exchange][market]:
                        for indicator in new_analysis[exchange][market][indicator_type]:
                            for index, analysis in enumerate(new_analysis[exchange][market][indicator_type][indicator]):
                                analysis_dict = analysis['result'].to_dict(orient='records')
                                if analysis_dict:
                                    new_analysis[exchange][market][indicator_type][indicator][index] = analysis_dict[-1]
                                else:
                                    new_analysis[exchange][market][indicator_type][indicator][index] = ''

            self.webhook_client.notify(new_analysis)

    def notify_stdout(self, new_analysis):
        """Send a notification via the stdout notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.stdout_configured:
            message = self._indicator_message_templater(
                new_analysis,
                self.notifier_config['stdout']['optional']['template']
            )
            if message.strip():
                self.stdout_client.notify(message)

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

                            # Save status of indicator's new analysis
                            new_analysis[exchange][market][indicator_type][indicator][index]['status'] = status

                            if latest_result['is_hot'] or latest_result['is_cold']:
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
                                        last_status=last_status
                                    )

        # Merge changes from new analysis into last analysis
        self.last_analysis = {**self.last_analysis, **new_analysis}
        return new_message
