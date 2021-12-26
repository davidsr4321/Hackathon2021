

import os
import socket
import sys
import threading
import time

import socket

from struct import *
from socket import *
import select

from Colors import Colors


class Client:
    def __init__(self):
        
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

def act_as_server(name):
    s = socket()
    s.bind(('', 12346))
    s.listen(5)
    c, addr = s.accept()
    print('Got connection from', addr)
    sys.stdout.flush()
    c.send(b'1+1=?')
    print("sending char to client")
    sys.stdout.flush()
    time.sleep(10)
    c.send(b'd')
    val = c.recv(128)
    print("recieved a message from client  ")
    print(val)
    c.close()

def main():
    # client = Client()
    # while True:
    #     client.run()
    x = threading.Thread(target=act_as_server, args=(1,))

    x.start()
    time.sleep(5)
    client_tcp_socket = socket()
    port = 12346
    data = None
    client_tcp_socket.connect(('127.0.0.1', port))
    time.sleep(1)
    question = client_tcp_socket.recv(1024)
    print(question.decode('utf-8'))
    # receive question from server and display it
    print("please enter input: ")
    sys.stdout.flush()

    client_tcp_socket.setblocking(False)
    inputs = [client_tcp_socket, sys.stdin]
    while inputs:
        readable, _, exceptional = select.select(inputs, [], inputs, 0.5)
        for s in readable:
            if s==sys.stdin:
                data =  sys.stdin.readline()
                client_tcp_socket.send(data.encode("utf-8"))
                break 
            if s==client_tcp_socket:
            # the client doesn't need to su[[ly any further input
                data = s.recv(1024)
                inputs.remove(s)
                inputs.remove(sys.stdin)
                exceptional.remove(s)
                break

        for s in exceptional:
            inputs.remove(s)
            break

    print(data)
    client_tcp_socket.close()
    sys.stderr.flush()



if __name__ == "__main__":
    main()
