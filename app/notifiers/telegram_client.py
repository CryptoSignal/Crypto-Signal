"""Notify a user via telegram
"""

import json

import telegram
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from notifiers.utils import NotifierUtils


class TelegramNotifier(NotifierUtils):
    """Used to notify user of events via telegram.
    """

    def __init__(self, token, chat_id, parse_mode):
        """Initialize TelegramNotifier class

        Args:
            token (str): The telegram API token.
            chat_id (str): The chat ID you want the bot to send messages to.
        """

        self.logger = structlog.get_logger()
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id
        self.parse_mode = parse_mode


    @retry(
        retry=retry_if_exception_type(telegram.error.TimedOut),
        stop=stop_after_attempt(3),
        wait=wait_fixed(5)
    )
    def notify(self, message):
        """Send the notification.

        Args:
            message (str): The message to send.
        """

        max_message_size = 4096
        message_chunks = self.chunk_message(message=message, max_message_size=max_message_size)
        #print(message_chunks)
        #exit()
        for message_chunk in message_chunks:
            self.bot.send_message(chat_id=self.chat_id, text=message_chunk, parse_mode=self.parse_mode)
