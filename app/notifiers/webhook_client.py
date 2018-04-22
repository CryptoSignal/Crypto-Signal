"""Notify another app via webhook
"""

import structlog

from notifiers.utils import NotifierUtils

class WebhookNotifier(NotifierUtils):
    """Class for handling webhook notifications
    """

    def __init__(self, url, auth_token):
        self.logger = structlog.get_logger()
        self.url = url
        self.auth_token = auth_token


    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.
        """

        pass
