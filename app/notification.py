"""
Handles sending notifications via the configured notifiers
"""

from notifiers.twilio import TwilioNotifier
from notifiers.slack import SlackNotifier
from notifiers.gmail import GmailNotifier

class Notifier():
    """
    Handles sending notifications via the configured notifiers
    """
    def __init__(self, config):
        self.twilio_configured = True
        for opt, val in config['notifiers']['twilio']['required'].items():
            if not val:
                self.twilio_configured = False
        if self.twilio_configured:
            self.twilio_client = TwilioNotifier(
                twilio_key=config['notifiers']['twilio']['required']['key'],
                twilio_secret=config['notifiers']['twilio']['required']['secret'],
                twilio_sender_number=config['notifiers']['twilio']['required']['sender_number'],
                twilio_receiver_number=config['notifiers']['twilio']['required']['receiver_number']
            )

        self.slack_configured = True
        for opt, val in config['notifiers']['slack']['required'].items():
            if not val:
                self.slack_configured = False
        if self.slack_configured:
            self.slack_client = SlackNotifier(
                slack_key=config['notifiers']['slack']['required']['key'],
                slack_channel=config['notifiers']['slack']['required']['channel']
            )

        self.gmail_configured = True
        for opt, val in config['notifiers']['gmail']['required'].items():
            if not val:
                self.gmail_configured = False
        if self.gmail_configured:
            self.gmail_client = GmailNotifier(
                username=config['notifiers']['gmail']['required']['username'],
                password=config['notifiers']['gmail']['required']['password'],
                destination_addresses=config['notifiers']['gmail']['required']['destination_emails']
            )

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
