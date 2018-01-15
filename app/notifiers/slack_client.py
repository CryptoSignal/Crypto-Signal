"""Notify a user via slack
"""

import structlog
import slackweb

class SlackNotifier():
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

        self.slack_client.notify(text=message)
