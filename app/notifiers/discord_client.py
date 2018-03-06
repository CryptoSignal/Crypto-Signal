
"""Notify a user via discord
"""

import structlog
from webcord import Webhook

class DiscordNotifier():
    """Class for handling Discord notifications
    """

    def __init__(self, webhook, avatar, username):
        """Initialize DiscordNotifier class

        Args:
            Discord_webhook (str): Discord web hook to allow message sending.
        """

        self.logger = structlog.get_logger()
        self.discord_username = username
        self.discord_client = Webhook(webhook, avatar_url=avatar)


    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.
        """

        self.discord_client.send_message(message, self.discord_username)
