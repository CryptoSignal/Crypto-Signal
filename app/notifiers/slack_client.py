"""Notify a user via slack
"""

import structlog
from slackclient import SlackClient

class SlackNotifier():
    """Class for handling slack notifications
    """

    def __init__(self, slack_key, slack_channel):
        """Initialize SlackNotifier class

        Args:
            slack_key (str): Slack API key to allow message sending.
            slack_channel (str): The slack channel to send the messages to.
        """

        self.logger = structlog.get_logger()
        self.slack_name = "crypto-signal"
        self.slack_channel = slack_channel
        self.slack_client = SlackClient(slack_key)


    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.
        """

        self.slack_client.api_call(
            "chat.postMessage",
            username=self.slack_name,
            channel=self.slack_channel,
            text=message)
