""" Utilities for notifiers
"""

import structlog

class NotifierUtils():
    """ Utilities for notifiers
    """

    def __init__(self):
        self.logger = structlog.get_logger()


    def chunk_message(self, message, max_message_size):
        """ Chunks message so that it meets max size of integration.

        Args:
            message (str): The message to chunk.
            max_message_size (int): The max message length for the chunks.

        Returns:
            list: The chunked message.
        """

        chunked_message = list()
        if len(message) > max_message_size:
            split_message = message.splitlines(keepends=True)
            chunk = ''

            for message_part in split_message:
                temporary_chunk = chunk + message_part

                if max_message_size > len(temporary_chunk):
                    chunk += message_part
                else:
                    chunked_message.append(chunk)
                    chunk = ''
        else:
            chunked_message.append(message)

        return chunked_message
