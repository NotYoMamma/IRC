
import threading 
import socket
import sys
import logging
from enum import Enum
import datetime
from Helpers import *

now = datetime.datetime.now()
logging.basicConfig(
    filename=''.join(["1.log"]),#issue with Windows path
	
    level=logging.INFO
)

ErrorCodes = Enum(
    'ErrorCodes',
    'UNKNOWN_HOST UNKNOWN_FAILURE UNKNOWN_CHANNEL UNKOWN_USER '
    'MESSAGE_SENT PONG_SUCCESS SERVER_CONNECTED HOSTNAME_NOT_RESOLVED '
    'SERVER_DISCONNECTED CHANNEL_JOINED CHANNEL_NAME_MALFORMED CHANNEL_LEFT '
)


#This thread doesn't stop correctly (I'll fix it later)
class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        readbuffer = ''
        while 1:
            data = client.connection.recv(4096)
           
            if data.find('PING') != -1: #Server periodically checks if client is ALIVE
                client.connection.send('PONG ' + data.split()[1] + '\r\n')
            elif data.find('PRIVMSG') != -1:
                nick = data.split('!')[0] + ':'
                message = nick[1:] + ':'.join(data.split(':')[2:])
                print(message)
            elif data.find('322') != -1:
                channel_string = ''
                #print(data)
                channels = data.split('322')
                for channel in channels:
                    if(channel.find('#') != -1):
                        channel_string = '#' + (channel.split('#')[1])
                        print(channel_string)
            elif data.find('NOTICE') != -1:
                print(data)
            elif not data:
                print("Connection closed") 

class Client(object):

    DEFAULT_PORT = 6667

    def __init__(self, username, host, port, password=None):
        self.user_name = username
        self.password = password
        self.host = host
        self.port = port
        self.connection = self.get_connection()
        self.channel = '' #Not sure if this belongs here 
        
    def set_channel(self, channel):
        self.channel = channel

    def get_connection(self ):
        s = socket.socket()
        s.connect((self.host, self.port))
        return s

    def connection_registration(self):
        if self.password is not None:
            pass_string = "PASS %s\r\n" % self.password

        nick_string = "NICK %s\r\n" % self.user_name
        user_string = "USER %s tester tster :testerirc\r\n" % self.user_name #Parameters: <username> <hostname> <servername> <realname>

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
			
						
username = raw_input("Enter username\n")
host = raw_input("Type in server address\n")
port = int(raw_input("port?\n"))
client = Client(username, host, port)	
client.connection_registration()

#Initiate worker thread
worker = Worker()
worker.Daemon = True
worker.start()

command = ''
while command != '/stop':
    command = raw_input()
    if command == '/help':
        print('This is help statement')
    elif command == '/list':
        send_message('LIST\r\n',client.connection)
    elif command == '/stop':
        worker.join()
    elif command.find('/join') != -1:
        params = command.split(' ')
        send_message('JOIN ' + params[1] + '\r\n',client.connection)
        client.set_channel(params[1])#This is a workaround
    elif command[0] == '/':
        print('Uknown command')
    else:
        send_message('PRIVMSG ' + client.channel + ' :' + command +'\r\n',client.connection)
			
