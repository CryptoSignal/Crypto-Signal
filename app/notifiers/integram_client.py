"""Notify a user via integram & telegram
"""

import json
import urllib.request

import structlog

class IntegramNotifier:
    """Used to notify user of event via integram.org bot webhook to telegram, Add @integram_bot
        to telegram and select webhooks.
    """

    def __init__(self, url):
        """Initialize IntegramNotifier class

        Args:
            url (str): The URL for the notification web hook.
        """

        self.logger = structlog.get_logger()
        self.url = url


    def notify(self, message):
        """Send the notification.

        Args:
            message (str): The message to send.
        """

        data = {"text":message}
        req = urllib.request.Request(self.url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(data)
        jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
        req.add_header('Content-Length', len(jsondataasbytes))
        urllib.request.urlopen(req, jsondataasbytes)
