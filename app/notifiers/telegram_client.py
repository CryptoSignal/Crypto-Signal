"""Notify a user via telegram
"""

import json

import structlog
import telegram
from telegram.utils.request import Request
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_fixed)

from notifiers.utils import NotifierUtils

__con_pool_size__ = 10
__connect_timeout__ = 40
__stop_after_attempt__ = 3
__wait_fixed__ = 5
__max_message_size__ = 4096

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
        self.bot = telegram.Bot(token=token, request=Request(
            con_pool_size=__con_pool_size__, connect_timeout=__connect_timeout__))
        self.chat_id = chat_id
        self.parse_mode = parse_mode

    @retry(
        retry=retry_if_exception_type(telegram.error.TimedOut),
        stop=stop_after_attempt(__stop_after_attempt__),
        wait=wait_fixed(__wait_fixed__)
    )
    def notify(self, message):
        """Send the notification.

        Args:
            message (str): The message to send.
        """
        message_chunks = self.chunk_message(
            message=message, max_message_size=__max_message_size__)
        for message_chunk in message_chunks:
            try:
                self.bot.send_message(
                    chat_id=self.chat_id, text=message_chunk, parse_mode=self.parse_mode)
            except Exception as e:
                self.logger.info('Unable to send message using Telegram !')
                self.logger.debug(e)

    @retry(
        retry=retry_if_exception_type(telegram.error.TimedOut),
        stop=stop_after_attempt(__stop_after_attempt__),
        wait=wait_fixed(__wait_fixed__)
    )
    def send_chart_messages(self, photo_url, messages=[]):
        """Send image chart

        Args:
            photo_url (str): The photo url to send.
        """
        self.bot.send_photo(chat_id=self.chat_id, photo=photo_url, timeout=40)
        self.send_messages(messages)

    def send_messages(self, messages=[]):
        if messages:
            for message in messages:
                self.notify(message)
