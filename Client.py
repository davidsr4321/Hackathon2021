
import sys
import threading
import time

from struct import *
from socket import *
import select

from Colors import Colors


class Client:
    CLIENT_STARTED_MESSAGE = Colors.colored_string("Client started, listening for offer requests...",Colors.OKCYAN)
    RECEIVED_ADDRESS_MSG = "Received offer from {address},attempting to connect..."
    FAILED_TO_CONNECT_TO_SERVER = Colors.colored_string("Couldn't connect to server ): ", Colors.WARNING)
    PACKING_FORMAT = 'IbH'
    UDP_DEST_PORT = 13117
    UTF_FORMAT = 'utf-8'
    BUFF_SIZE = 1024
    MAGIC_COOKIE = 0xabcddcba
    MSG_TYPE = 0x2
    SELECT_TIMEOUT = 0.5


    def __init__(self):
        self.tcp_socket = None
        self.udp_socket = None
    
    # in the first stage the client will receive a udp broadcast, and decrypt it
    def firstStage(self):
        print(self.CLIENT_STARTED_MESSAGE)
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_socket.bind(('', self.UDP_DEST_PORT))
        while 1:
            data, addr = self.udp_socket.recvfrom(self.BUFF_SIZE)  # buffer size is 1024 bytes
            magic_cookie, msg_type, server_port = unpack(self.PACKING_FORMAT, data)
            if (magic_cookie == self.MAGIC_COOKIE) & (msg_type == self.MSG_TYPE):
                msg = self.RECEIVED_ADDRESS_MSG
                msg.format(**{"address": addr})
                msg = Colors.colored_string(msg, Colors.OKGREEN)
                print(msg)
                self.udp_socket.close()
                return addr, server_port


    def thirdStage(self):
        # first thing first: recieve and display the question 
        question = self.tcp_socket.recv(self.BUFF_SIZE)
        print(question.decode(self.UTF_FORMAT))
        
        #set the socket to non-blocking in irder to work in paraller
        self.tcp_socket.setblocking(False)
        inputs = [self.tcp_socket, sys.stdin]
        while inputs:
            # each iteration we will poll info from the sockets, if there is anything to read it will be in 
            readables, _, exceptional = select.select(inputs, [], inputs, self.SELECT_TIMEOUT)
            for s in readables:
                if s==sys.stdin:
                    # recieve data from user and send it to the server 
                    userInput =  sys.stdin.readline()
                    self.tcp_socket.send(userInput.encode(self.UTF_FORMAT))
                    break 
            
                if s==self.tcp_socket:
                    # recieve data from server -> the game is over 
                    data = s.recv(self.BUFF_SIZE)
                    inputs.remove(s)
                    inputs.remove(sys.stdin)
                    break

            for s in exceptional:
                inputs.remove(s)
                break

        print(data.decode(self.UTF_FORMAT))
        self.tcp_socket.close()

    def run(self):
        while True:
            # first stage: find an offer
            server_addr, server_port = self.firstStage()

            # second stage: try to connect to serve
            self.tcp_socket = socket(AF_INET, SOCK_STREAM)
            try:
                self.tcp_socket.connect(server_addr, server_port)
            except socket.error:  # if the connection has failed
                print(self.FAILED_TO_CONNECT_TO_SERVER)
            else:
                # third stage
                self.thirdStage()

def main():
    client = Client()
    client.run()
    
if __name__ == "__main__":
    main()
