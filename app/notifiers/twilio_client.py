"""Notify a user via twilio
"""

import structlog
from twilio.rest import Client

from notifiers.utils import NotifierUtils


class TwilioNotifier(NotifierUtils):
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

        max_message_size = 1600
        message_chunks = self.chunk_message(
            message=message, max_message_size=max_message_size)

        for message_chunk in message_chunks:
            self.twilio_client.api.account.messages.create(
                to=self.twilio_receiver_number,
                from_=self.twilio_sender_number,
                body=message_chunk
            )
