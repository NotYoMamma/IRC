import socket
import logging
import enum
import datetime
from Helpers import *

now = datetime.datetime.now()
logging.basicConfig(
    filename=''.join(["Logs/", str(datetime.datetime.now()), ".log"]),
    level=logging.INFO
)

ErrorCodes = enum(
    'ErrorCodes',
    'UNKNOWN_HOST UNKNOWN_FAILURE UNKNOWN_CHANNEL UNKOWN_USER '
    'MESSAGE_SENT PONG_SUCCESS SERVER_CONNECTED HOSTNAME_NOT_RESOLVED '
    'SERVER_DISCONNECTED CHANNEL_JOINED CHANNEL_NAME_MALFORMED CHANNEL_LEFT '
)


class Client(object):

    DEFAULT_PORT = 6667

    def __init__(self, username, host, port, password=None):
        self.user_name = username
        self.password = password
        self.host = host
        self.port = port
        self.connection = self.get_connection()

    def get_connection(self ):
        s = socket.socket()
        s.connect(self.host, self.port)
        return s

    def connection_registration(self):
        if self.password is not None:
            pass_string = "PASS %s\r\n" % self.password

        nick_string = "NICK %s\r\n" % self.user_name
        user_string = "USER %s\r\n" % self.user_name

        try:

            if self.password is not None:
                send_message(pass_string, self.connection)

            send_message(nick_string, self.connection)
            send_message(user_string, self.connection)

        except socket.gaierror as e:
            logging.exception(e)
            return ErrorCodes.HOSTNAME_NOT_RESOLVED

        except socket.error as e:
            logging.exception(e)
            if self.port != self.DEFAULT_PORT:
                logging.warning(
                    "Consider using port %s (the defacto IRC port) not of %s"
                        % (self.DEFAULT_PORT, self.port)
                )
            return ErrorCodes.UNKNOWN_FAILURE

        else:
            logging.info("Connected to {} on {}".format(self.host, self.port))
            return ErrorCodes.SERVER_CONNECTED
