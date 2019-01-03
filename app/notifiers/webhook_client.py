"""Notify another app via webhook
"""

import os
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


    def notify(self, exchange, market_pair, candle_period, messages, send_charts):
        """Sends the notification messages.

        Args:
            messages (dict): A dict with the messages to send.
        """

        market_pair = market_pair.replace('/', '_').lower()
        chart_file = '{}/{}_{}_{}.png'.format('./charts', exchange, market_pair, candle_period)        

        if send_charts == True and os.path.exists(chart_file):
            files = {'chart': open(chart_file, 'rb')}

            if self.username and self.password:
                request = requests.post(self.url, files=files, json=messages, auth=(self.username, self.password))
            else:
                request = requests.post(self.url, files=files, json=messages)
        else:
            if self.username and self.password:
                request = requests.post(self.url, json=messages, auth=(self.username, self.password))
            else:
                request = requests.post(self.url, json=messages)            

        if not request.status_code == requests.codes.ok:
            self.logger.error("Request failed: %s - %s", request.status_code, request.content)
