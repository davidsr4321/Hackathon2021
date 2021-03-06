
import sys
import termios
import tty

from struct import *
from socket import *
import select

from Colors import Colors


class Client:
    CLIENT_STARTED_MESSAGE = Colors.colored_string("Client started, listening for offer requests...",Colors.OKCYAN)
    CLIENT_CONTINUE_MESSAGE = Colors.colored_string("\nlistening for offer requests...",Colors.OKCYAN)
    LISTENING_MESSAGE = Colors.colored_string("Listening for offer requests...",Colors.OKCYAN)
    RECEIVED_ADDRESS_MSG = "\nReceived offer from {address},attempting to connect...\n"
    FAILED_TO_CONNECT_TO_SERVER = Colors.colored_string("Couldn't connect to server ): ", Colors.WARNING)
    CONNECTION_ERROR = Colors.colored_string("We are sorry to inform you that there were a connection problems ): ", Colors.WARNING)
    YOU_PRESSED = Colors.colored_string("\nYou pressed: {char}\n",Colors.UNDERLINE)
    EXIT_MSG= Colors.colored_string("thank you for playing !",Colors.HEADER)
    TEAM_NAME = "pACKistan\n"
    PACKING_FORMAT = '>IbH' #TODO
    DEV_IP_PREFIX = '172.1.'
    TEST_IP_PREFIX = '172.99.'
    UDP_DEST_PORT = 13117 #TODO
    UTF_FORMAT = 'utf-8'
    TCP_BUFF_SIZE = 1024
    UDP_BUFF_SIZE = 7
    MAGIC_COOKIE = 0xabcddcba
    MSG_TYPE = 0x2
    SELECT_TIMEOUT = 0.5


    def __init__(self):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1) # TODO: DELETE WHEN NOT TESTING!
        self.udp_socket.bind(('', self.UDP_DEST_PORT))
        self.tcp_socket = None
    
    # in the first stage the client will receive a udp broadcast, and decrypt it
    def find_offer(self):
        while 1:
            if self.udp_socket!=None:
                data, addr = self.udp_socket.recvfrom(self.UDP_BUFF_SIZE)
            try:
                magic_cookie, msg_type, server_port = unpack(self.PACKING_FORMAT, data)
            except:
                return None, None
            if (magic_cookie == self.MAGIC_COOKIE) & (msg_type == self.MSG_TYPE):
                msg = self.RECEIVED_ADDRESS_MSG
                msg = msg.format(**{"address": addr})
                msg = Colors.colored_string(msg, Colors.OKGREEN)
                print(msg)
                return addr[0], server_port

    def play_game(self):
        sent_length = self.tcp_socket.send(self.TEAM_NAME.encode(self.UTF_FORMAT))
        if sent_length == 0:
            print(self.CONNECTION_ERROR)
            return None

        # recieve and display the question 
        question = self.tcp_socket.recv(self.TCP_BUFF_SIZE)
        print(question.decode(self.UTF_FORMAT))
        
        # set the socket to non-blocking in order to work in paraller
        self.tcp_socket.setblocking(False)
        inputs = [self.tcp_socket, sys.stdin]
        previous_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        try:
            while inputs:
                # each iteration we will poll info from the sockets, if there is anything to read it will be in 
                readables, _, exceptional = select.select(inputs, [], inputs, self.SELECT_TIMEOUT)
                for s in readables:
                    if s==sys.stdin:
                        # recieve data from user and send it to the server 
                        userInput = sys.stdin.read(1)
                        msg = self.YOU_PRESSED
                        msg = msg.format(**{"char": userInput})
                        msg = Colors.colored_string(msg, Colors.OKGREEN)
                        print(msg)
                        self.tcp_socket.send(userInput.encode(self.UTF_FORMAT))
                        break 
                
                    if s==self.tcp_socket:
                        # recieve data from server -> the game is over 
                        data = s.recv(self.TCP_BUFF_SIZE)
                        print(data.decode(self.UTF_FORMAT))
                        inputs.remove(s)
                        inputs.remove(sys.stdin)
                        break

                for s in exceptional:
                    inputs.remove(s)
                    break
        except error: 
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, previous_settings)
            self.tcp_socket.close()
            raise(error)
        else:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, previous_settings)
            self.tcp_socket.close()

    def run(self):
        print(self.CLIENT_STARTED_MESSAGE)
        while True:
            try:
                # first stage: find an offer
                server_addr, server_port = self.find_offer()
                if (server_addr!=None):
                    # second stage: try to connect to serve
                    comp = server_addr.split('.')
                    server_addr = self.TEST_IP_PREFIX + comp[2] + "." + comp[3]
                    self.tcp_socket = socket(AF_INET, SOCK_STREAM)
                    try:
                        self.tcp_socket.connect((server_addr, server_port))
                    except error:  # if the connection has failed
                        print(self.FAILED_TO_CONNECT_TO_SERVER)
                        print(self.CLIENT_CONTINUE_MESSAGE)
                    else:
                        # third stage
                        self.play_game()
                        print(self.CLIENT_CONTINUE_MESSAGE)
            except KeyboardInterrupt:
                self.close()
                print(self.EXIT_MSG)
                break            
            
            except error:
                self.close()

    def close(self):
        try:
            self.udp_socket.close()
        except error:
            pass
       
        try:
            if self.tcp_socket != None:
                self.tcp_socket.close()
        except error:
            pass

    def receive_string_message(self, socket, size, timeout=None, encoding=UTF_FORMAT):
        if timeout != None:
            socket.settimeout(timeout)
        try:
            bytes = socket.recv(size)
            return bytes.decode(encoding)
        except error:
            return None


def main():
    client = Client()
    client.run()
    
if __name__ == "__main__":
    main()
