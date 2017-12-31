import structlog
import smtplib

class GmailNotifier:
    def __init__(self, username, password, destination_addresses):
        self.logger = structlog.get_logger()
        smtp_server = 'smtp.gmail.com:587'
        self.smtp_handler = smtplib.SMTP(smtp_server)
        self.username = username
        self.password = password
        self.destination_addresses = destination_addresses

    def notify(self, message):
        """
        Used to send an email from the account specified in the secrets.json file to the entire
        address list specified in the secrets.json file

        :param subject: Email subject
        :type subject: str
        :param message: Email content
        :type message: str

        :return: Errors received from the smtp server (if any)
        :rtype : dict
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
