"""
Handles sending notifications via the configured notifiers
"""

import structlog
from notifiers.twilio import TwilioNotifier
from notifiers.slack import SlackNotifier
from notifiers.gmail import GmailNotifier

class Notifier():
    """
    Handles sending notifications via the configured notifiers
    """
    def __init__(self, notifier_config):
        self.logger = structlog.get_logger()
        self.twilio_configured = self.__validate_required_config('twilio', notifier_config)
        if self.twilio_configured:
            self.twilio_client = TwilioNotifier(
                twilio_key=notifier_config['twilio']['required']['key'],
                twilio_secret=notifier_config['twilio']['required']['secret'],
                twilio_sender_number=notifier_config['twilio']['required']['sender_number'],
                twilio_receiver_number=notifier_config['twilio']['required']['receiver_number']
            )

        self.slack_configured = self.__validate_required_config('slack', notifier_config)
        if self.slack_configured:
            self.slack_client = SlackNotifier(
                slack_key=notifier_config['slack']['required']['key'],
                slack_channel=notifier_config['slack']['required']['channel']
            )

        self.gmail_configured = self.__validate_required_config('gmail', notifier_config)
        if self.gmail_configured:
            self.gmail_client = GmailNotifier(
                username=notifier_config['gmail']['required']['username'],
                password=notifier_config['gmail']['required']['password'],
                destination_addresses=notifier_config['gmail']['required']['destination_emails']
            )

    def __validate_required_config(self, notifier, notifier_config):
        notifier_configured = True
        for opt, val in notifier_config[notifier]['required'].items():
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
