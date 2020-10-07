"""Notify a user via Gmail
"""

import smtplib

import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from notifiers.utils import NotifierUtils

class GmailNotifier(NotifierUtils):
    """Class for handling gmail notifications
    """

    def __init__(self, username, password, destination_addresses):
        """Initialize GmailNotifier class

        Args:
            username (str): Username of the gmail account to use for sending message.
            password (str): Password of the gmail account to use for sending message.
            destination_addresses (list): A list of email addresses to notify.
        """

        self.logger = structlog.get_logger()
        self.smtp_server = 'smtp.gmail.com:587'
        self.username = username
        self.password = password
        self.destination_addresses = ','.join(destination_addresses)


    @retry(stop=stop_after_attempt(3))
    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.

        Returns:
            dict: A dictionary containing the result of the attempt to send the email.
        """

        header = 'From: %s\n' % self.username
        header += 'To: %s\n' % self.destination_addresses
        header += 'Content-Type: text/plain\n'
        header += 'Subject: Crypto-signal alert!\n\n'
        message = header + message

        smtp_handler = smtplib.SMTP(self.smtp_server)
        smtp_handler.starttls()
        smtp_handler.login(self.username, self.password)
        result = smtp_handler.sendmail(self.username, self.destination_addresses, message)
        smtp_handler.quit()
        return result
