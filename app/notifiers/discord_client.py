
"""Notify a user via discord
"""

import structlog
from webcord import Webhook


class DiscordNotifier():
    """Class for handling Discord notifications
    """

    def __init__(self, webhook, username, avatar=None):
        """Initialize DiscordNotifier class

        Args:
            webhook (str): Discord web hook to allow message sending.
            username (str): Display name for the discord bot.
            avatar (str, optional): Defaults to None. Url of an image to use as an avatar.
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
