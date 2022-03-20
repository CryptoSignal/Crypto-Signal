
"""Notify a user via discord
"""

import structlog
from discord_webhook import DiscordWebhook as Webhook

from notifiers.utils import NotifierUtils

class DiscordNotifier(NotifierUtils):
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
        self.discord_client = Webhook(url=webhook, username=username, avatar_url=avatar, rate_limit_retry=True)

    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.
        """

        max_message_size = 2000
        message_chunks = self.chunk_message(
            message=message, max_message_size=max_message_size)
        # print(message_chunks)
        # exit()
        for message_chunk in message_chunks:
            try:
                self.discord_client.set_content(message_chunk)
                self.discord_client.execute()
            except Exception as e:
                self.logger.info('Unable to send message using Discord !')
                self.logger.info('Check your configuration ...')
                self.logger.debug(e)
                exit(0)

    def send_chart_messages(self, photo_url, messages=[]):
        """Send image chart
        Args:
            photo_url (str): The photo url to send.
        """

        self.discord_client.set_content("")
        self.discord_client.add_file(file=photo_url.read(), filename=photo_url.name)
        self.discord_client.execute(remove_files=True)

        if len(messages) > 0:
            for message in messages:
                self.notify(message)

    def send_messages(self, messages=[]):
        if len(messages) > 0:
            for message in messages:
                self.notify(message)
