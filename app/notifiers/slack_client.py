"""
Used to notify user of event via slack
"""

import structlog
from slackclient import SlackClient

class SlackNotifier():
    """
    Used to notify user of event via twilio
    """
    def __init__(self, slack_key, slack_channel):
        self.logger = structlog.get_logger()
        self.slack_name = "crypto-signal"
        self.slack_channel = slack_channel
        self.slack_client = SlackClient(slack_key)

    def notify(self, message):
        """
        Send notification to user
        """
        self.slack_client.api_call(
            username=self.slack_name,
            channel=self.slack_channel,
            text=message)
