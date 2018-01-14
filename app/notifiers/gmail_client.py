"""Notify a user via Gmail
"""

import smtplib

import structlog

class GmailNotifier:
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
        smtp_server = 'smtp.gmail.com:587'
        self.smtp_handler = smtplib.SMTP(smtp_server)
        self.username = username
        self.password = password
        self.destination_addresses = ','.join(destination_addresses)

    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.

        Returns:
            dict: A dictionary containing the result of the attempt to send the email.
        """

        header = 'From: %s\n' % self.username
        header += 'To: %s\n' % self.destination_addresses
        header += 'Subject: Crypto-signal alert!\n\n'
        message = header + message

        self.smtp_handler.starttls()
        self.smtp_handler.login(self.username, self.password)
        result = self.smtp_handler.sendmail(self.username, self.destination_addresses, message)
        self.smtp_handler.quit()
        return result
