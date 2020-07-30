"""Notify a user via slack
"""

import slackweb
import structlog

from notifiers.utils import NotifierUtils


class SlackNotifier(NotifierUtils):
    """Class for handling slack notifications
    """

    def __init__(self, slack_webhook):
        """Initialize SlackNotifier class

        Args:
            slack_webhook (str): Slack web hook to allow message sending.
        """

        self.logger = structlog.get_logger()
        self.slack_name = "crypto-signal"
        self.slack_client = slackweb.Slack(url=slack_webhook)

    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.
        """

        max_message_size = 4096
        message_chunks = self.chunk_message(
            message=message, max_message_size=max_message_size)

        for message_chunk in message_chunks:
            self.slack_client.notify(text=message_chunk)
