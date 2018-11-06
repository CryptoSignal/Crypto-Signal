"""Notify another app via webhook
"""

import structlog
import requests

from notifiers.utils import NotifierUtils

class WebhookNotifier(NotifierUtils):
    """Class for handling webhook notifications
    """

    def __init__(self, url, username, password):
        self.logger = structlog.get_logger()
        self.url = url
        self.username = username
        self.password = password


    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.
        """

        if self.username and self.password:
            request = requests.post(self.url, json=message, auth=(self.username, self.password))
        else:
            request = requests.post(self.url, json=message)

        if not request.status_code == requests.codes.ok:
            self.logger.error("Request failed: %s - %s", request.status_code, request.content)
