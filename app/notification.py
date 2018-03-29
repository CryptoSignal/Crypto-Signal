"""Handles sending notifications via the configured notifiers
"""

import structlog
from jinja2 import Template

from notifiers.twilio_client import TwilioNotifier
from notifiers.slack_client import SlackNotifier
from notifiers.discord_client import DiscordNotifier
from notifiers.gmail_client import GmailNotifier
from notifiers.telegram_client import TelegramNotifier

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
                chat_id=notifier_config['telegram']['required']['chat_id']
            )
            enabled_notifiers.append('telegram')

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


    def notify_discord(self, new_analysis):
        """Send a notification via the discord notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.discord_configured:
            message = self._message_templater(
                new_analysis,
                self.notifier_config['discord']['optional']['template']
            )
            self.discord_client.notify(message)


    def notify_slack(self, new_analysis):
        """Send a notification via the slack notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.slack_configured:
            message = self._message_templater(
                new_analysis,
                self.notifier_config['slack']['optional']['template']
            )
            self.slack_client.notify(message)


    def notify_twilio(self, new_analysis):
        """Send a notification via the twilio notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.twilio_configured:
            message = self._message_templater(
                new_analysis,
                self.notifier_config['twilio']['optional']['template']
            )
            self.twilio_client.notify(message)


    def notify_gmail(self, new_analysis):
        """Send a notification via the gmail notifier

        Args:
            new_analysis (dict): The new_analysis to send.
        """

        if self.gmail_configured:
            message = self._message_templater(
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
            message = self._message_templater(
                new_analysis,
                self.notifier_config['telegram']['optional']['template']
            )
            self.telegram_client.notify(message)


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


    def _message_templater(self, new_analysis, template):
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
                for analyzer in new_analysis[exchange][market]:
                    for index, indicator in enumerate(new_analysis[exchange][market][analyzer]):
                        formatted_values = list()
                        for value in indicator['result']['values']:
                            if isinstance(value, float):
                                formatted_values.append(format(value, '.8f'))
                            else:
                                formatted_values.append(value)
                        formatted_string = '/'.join(formatted_values)

                        status = 'neutral'
                        if indicator['result']['is_hot']:
                            status = 'hot'
                        elif indicator['result']['is_cold']:
                            status = 'cold'

                        if indicator['result']['is_hot'] or indicator['result']['is_cold']:
                            try:
                                last_status = self.last_analysis[exchange][market][analyzer][index]['status']
                            except:
                                last_status = str()

                            if last_status != status:
                                new_analysis[exchange][market][analyzer][index]['status'] = status
                                new_message += message_template.render(
                                    exchange=exchange,
                                    market=market,
                                    analyzer=analyzer,
                                    analyzer_number=index,
                                    raw_values=indicator['result']['values'],
                                    raw_hot_value=indicator['result']['is_hot'],
                                    raw_cold_value=indicator['result']['is_cold'],
                                    string_values=formatted_string,
                                    status=status,
                                    user_config=indicator['config']
                                )

        # Merge changes from new analysis into last analysis
        self.last_analysis = {**self.last_analysis, **new_analysis}
        return new_message


