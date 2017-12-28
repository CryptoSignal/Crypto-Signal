
"""
Used to notify user of event via twilio
"""

from twilio.rest import Client

class TwilioNotifier():
    """
    Used to notify user of event via twilio
    """
    def __init__(self, twilio_key, twilio_secret, twilio_sender_number, twilio_receiver_number):
        self.twilio_sender_number = twilio_sender_number
        self.twilio_receiver_number = twilio_receiver_number
        self.twilio_client = Client(twilio_key, twilio_secret)

    def notify(self, message):
        """
        Send notification to user
        """
        self.twilio_client.api.account.messages.create(
            to=self.twilio_receiver_number,
            from_=self.twilio_sender_number,
            body=message)
