"""Handles sending notifications via the configured notifiers
"""

import structlog

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

        enabled_notifiers = []
        self.logger = structlog.get_logger()
        self.twilio_configured = self.__validate_required_config('twilio', notifier_config)
        if self.twilio_configured:
            self.twilio_client = TwilioNotifier(
                twilio_key=notifier_config['twilio']['required']['key'],
                twilio_secret=notifier_config['twilio']['required']['secret'],
                twilio_sender_number=notifier_config['twilio']['required']['sender_number'],
                twilio_receiver_number=notifier_config['twilio']['required']['receiver_number']
            )
            enabled_notifiers.append('twilio')

        self.discord_configured = self.__validate_required_config('discord', notifier_config)
        if self.discord_configured:
            self.discord_client = DiscordNotifier(
                webhook=notifier_config['discord']['required']['webhook'],
                username=notifier_config['discord']['required']['username'],
                avatar=notifier_config['discord']['optional']['avatar']
            )

        self.slack_configured = self.__validate_required_config('slack', notifier_config)
        if self.slack_configured:
            self.slack_client = SlackNotifier(
                slack_webhook=notifier_config['slack']['required']['webhook']
            )
            enabled_notifiers.append('slack')

        self.gmail_configured = self.__validate_required_config('gmail', notifier_config)
        if self.gmail_configured:
            self.gmail_client = GmailNotifier(
                username=notifier_config['gmail']['required']['username'],
                password=notifier_config['gmail']['required']['password'],
                destination_addresses=notifier_config['gmail']['required']['destination_emails']
            )
            enabled_notifiers.append('gmail')

        self.telegram_configured = self.__validate_required_config('telegram', notifier_config)
        if self.telegram_configured:
            self.telegram_client = TelegramNotifier(
                token=notifier_config['telegram']['required']['token'],
                chat_id=notifier_config['telegram']['required']['chat_id']
            )
            enabled_notifiers.append('telegram')

        self.logger.info('enabled notifers: %s', enabled_notifiers)


    def __validate_required_config(self, notifier, notifier_config):
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


    def notify_all(self, message):
        """Trigger a notification for all notification options.

        Args:
            message (str): The message to send.
        """

        if message.strip() is not '':
            self.notify_slack(message)
            self.notify_discord(message)
            self.notify_twilio(message)
            self.notify_gmail(message)
            self.notify_telegram(message)


    def notify_discord(self, message):
        """Send a notification via the discord notifier

        Args:
            message (str): The message to send.
        """

        if self.discord_configured:
            self.discord_client.notify(message)


    def notify_slack(self, message):
        """Send a notification via the slack notifier

        Args:
            message (str): The message to send.
        """

        if self.slack_configured:
            self.slack_client.notify(message)


    def notify_twilio(self, message):
        """Send a notification via the twilio notifier

        Args:
            message (str): The message to send.
        """

        if self.twilio_configured:
            self.twilio_client.notify(message)


    def notify_gmail(self, message):
        """Send a notification via the gmail notifier

        Args:
            message (str): The message to send.
        """

        if self.gmail_configured:
            self.gmail_client.notify(message)


    def notify_telegram(self, message):
        """Send a notification via the telegram notifier

        Args:
            message (str): The message to send.
        """

        if self.telegram_configured:
            self.telegram_client.notify(message)
