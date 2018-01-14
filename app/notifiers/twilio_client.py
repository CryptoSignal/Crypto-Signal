
"""Notify a user via twilio
"""

import structlog
from twilio.rest import Client

class TwilioNotifier():
    """Class for handling twilio notifications
    """

    def __init__(self, twilio_key, twilio_secret, twilio_sender_number, twilio_receiver_number):
        """Initialize TwilioNotifer class

        Args:
            twilio_key (str): They API key for authenticating to twilio.
            twilio_secret (str): They API secret for authenticating to twilio.
            twilio_sender_number (str): The twilio sender number to use.
            twilio_receiver_number (str): The user recipient number.
        """

        self.logger = structlog.get_logger()
        self.twilio_sender_number = twilio_sender_number
        self.twilio_receiver_number = twilio_receiver_number
        self.twilio_client = Client(twilio_key, twilio_secret)


    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.
        """

        self.twilio_client.api.account.messages.create(
            to=self.twilio_receiver_number,
            from_=self.twilio_sender_number,
            body=message)
