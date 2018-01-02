"""
Handles sending notifications via the configured notifiers
"""

import structlog
from notifiers.twilio_client import TwilioNotifier
from notifiers.slack_client import SlackNotifier
from notifiers.gmail_client import GmailNotifier

class Notifier():
    """
    Handles sending notifications via the configured notifiers
    """
    def __init__(self, config):
        self.logger = structlog.get_logger()
        self.twilio_configured = self.__validate_required_config('twilio', config)
        if self.twilio_configured:
            self.twilio_client = TwilioNotifier(
                twilio_key=config['notifiers']['twilio']['required']['key'],
                twilio_secret=config['notifiers']['twilio']['required']['secret'],
                twilio_sender_number=config['notifiers']['twilio']['required']['sender_number'],
                twilio_receiver_number=config['notifiers']['twilio']['required']['receiver_number']
            )

        self.slack_configured = self.__validate_required_config('slack', config)
        if self.slack_configured:
            self.slack_client = SlackNotifier(
                slack_key=config['notifiers']['slack']['required']['key'],
                slack_channel=config['notifiers']['slack']['required']['channel']
            )

        self.gmail_configured = self.__validate_required_config('gmail', config)
        if self.gmail_configured:
            self.gmail_client = GmailNotifier(
                username=config['notifiers']['gmail']['required']['username'],
                password=config['notifiers']['gmail']['required']['password'],
                destination_addresses=config['notifiers']['gmail']['required']['destination_emails']
            )

    def __validate_required_config(self, notifier, config):
        notifier_configured = True
        for opt, val in config['notifiers'][notifier]['required'].items():
            if not val:
                notifier_configured = False
        return notifier_configured

    def notify_all(self, message):
        """
        Triggers the notification with all configured notifiers
        """
        self.notify_slack(message)
        self.notify_twilio(message)
        self.notify_gmail(message)

    def notify_slack(self, message):
        """
        Triggers the notification to slack
        """
        if self.slack_configured:
            self.slack_client.notify(message)


    def notify_twilio(self, message):
        """
        Triggers the notification to slack
        """
        if self.twilio_configured:
            self.twilio_client.notify(message)

    def notify_gmail(self, message):
        """
        Triggers the notification via email using gmail
        """
        if self.gmail_configured:
            self.gmail_client.notify(message)
