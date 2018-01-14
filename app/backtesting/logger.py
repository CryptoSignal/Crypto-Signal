from datetime import datetime
from time import time


class Logger(object):

    @staticmethod
    def timestamp():
        return "[ " + datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S') + " ]\t"

    @staticmethod
    def log(message, type="info"):
        return
        timestamp = Logger.timestamp()

        message = timestamp + message

        if type == "success":
            message = "\033[92m" + message
        elif type == "error":
            message = "\033[91m" + message

        message += "\033[0m"

        print(message)