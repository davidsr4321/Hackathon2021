import msvcrt
import os
import socket
import sys
import threading
import time

import numpy as np
import socket

from struct import *
from socket import *
import select
import fileinput

from Colors import Colors


class Client:

    def __init__(self):
        self.CLIENT_STARTED_MESSAGE = Colors.colored_string("Client started, listening for offer requests...",Colors.OKCYAN)
        self.RECEIVED_ADDRESS_MSG = "Received offer from {address},attempting to connect..."
        self.FAILED_TO_CONNECT_TO_SERVER = Colors.colored_string("Couldn't connect to server ): ", Colors.WARNING)

    # in the first stage the client will receive a udp broadcast, and encrypt it
    def firstStage(self):
        print(self.CLIENT_STARTED_MESSAGE)
        client_udp_socket = socket(AF_INET, SOCK_DGRAM)
        server_udp_dst_port = 13117
        client_udp_socket.bind(('', server_udp_dst_port))
        while 1:
            data, addr = client_udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
            magic_cookie, msg_type, server_port = unpack('IbH', data)
            if (magic_cookie == 0xabcddcba) & (msg_type == 0x2):
                msg = self.RECEIVED_ADDRESS_MSG
                msg.format(**{"address": addr})
                msg = Colors.colored_string(msg, Colors.OKGREEN)
                print(msg)
                client_udp_socket.close()
                return addr, server_port

        pass

    def recv_from_socket(self, socket, flag):
        data = socket.recv(1024)
        print(data)
        flag.set()
        pass

    def recv_from_user(self, socket):
        userInfo = input()
        socket.send(userInfo.encode("utf-8"))
        pass

    def run(self):
        # first stage: find an offer
        server_addr, server_port = self.firstStage()

        # second stage: try to connect to server
        client_tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            client_tcp_socket.connect(server_addr, server_port)
        except socket.error:  # if the connection has failed
            print(self.FAILED_TO_CONNECT_TO_SERVER)
        else:
            # third stage
            question = client_tcp_socket.recv(1024)
            print(question)
            flag = threading.Event()
            thread0 = threading.Thread(target=self.recv_from_user, args=[client_tcp_socket])
            thread1 = threading.Thread(target=self.recv_from_socket, args=[client_tcp_socket, flag])
            thread0.start()
            thread1.start()
            flag.wait()
    pass


def main():
    client = Client()
    while True:
        client.run()



if __name__ == "__main__":
    main()
