"""Notify a user via stdout
"""

import structlog

from notifiers.utils import NotifierUtils

#from tenacity import retry, retry_if_exception_type, stop_after_attempt


class StdoutNotifier(NotifierUtils):
    """Class for handling stdout notifications
    """

    def __init__(self):
        """Initialize StdoutNotifier class
        """

    def notify(self, message):
        """stdout send the message.

        Args:
            message (str): The message to print.
        """

        print(message)
