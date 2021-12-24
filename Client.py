import numpy as np
from socket import *
from struct import *


class Client:
    def __init__(self, clientPort):
        self.clientPort = clientPort
        pass

    # in the first stage the client will recieve a udp broadcast, and encrypt it
    def firstStage(self):
        client_udp_socket = socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_udp_dst_port = 13117
        client_udp_socket.bind(('', server_udp_dst_port))
        while 1:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            magic_cookie, msg_type, server_port  = unpack('IbH', data)
            if (magic_cookie == 0xabcddcba) & (msg_type == 0x2):
                return addr, server_port

    pass
    def act(self):
        # first stage: find an offer
        server_addr, server_port =  firstStage()

        #second stage: try to connect to server
        client_tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            client_tcp_socket.connect(server_addr, server_port)
        except socket.error as msg: #if the connection has failed
            print(f"Failed to connect: {msg}")
        else:
            d

    pass

def main():
    var = pack('IbH', 0xabcddcba,  0x2, 1212)
    magic_cookie, msg_type, server_port  = unpack('IbH', var)
    print("magic is: %s, type is: %c, port is: %d" % (magic_cookie, msg_type, server_port))
    if  (magic_cookie ==  0xabcddcba) & (msg_type == 0x2):
            print('ok')


if __name__ == "__main__":
    main()