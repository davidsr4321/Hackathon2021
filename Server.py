import threading
import time
from struct import *
from socket import *
from threading import *
import scapy.all as sp
import RandomQuestionGenerator as rqg
from Colors import Colors
from Statistics import Statistics


class Server:
    BROADCAST_DEST_PORT = 13117
    MAGIC_COOKIE = 0xabcddcba
    MESSAGE_TYPE = 0X2
    PLAYERS_COUNT = 2
    ANSWER_SIZE = 1 # byte
    GAME_DURATION = 10  # seconds
    BROADCAST_TIME_INTERVAL = 1 # seconds
    BROADCAST_DEST_IP = '172.99.255.255'
    DEV_NETWORK = 'eth1'
    TEST_NETWORK = 'eth2'
    ENCODING = 'utf8'
    PACKING_FORMAT = 'IbH'
    WAITING_FOR_NAME_TIME = 5 # seconds
    END_OF_NAME = '\n'
    SERVER_START_MESSAGE = Colors.colored_string("Server started, listening on IP address ", Colors.HEADER)
    GAME_WELCOME_MESSAGE = Colors.colored_string("Welcome to Quick Maths.\nPlayer 1: {name0}\nPlayer 2: {name1}\n==\nPlease answer the following question as fast as you can:\n{question}", Colors.OKBLUE)
    GAME_END_WINNER_MESSAGE = Colors.colored_string("Game over!\nThe correct answer was {answer}!\nCongratulations to the winner: {winner}", Colors.OKCYAN)
    GAME_END_DRAW_MESSAGE = Colors.colored_string("Game over!\nThe correct answer was {answer}!\nWe have a draw!", Colors.OKCYAN)
    GAME_OVER_MESSAGE = Colors.colored_string("Game over, sending out offer requests...", Colors.OKBLUE)
    CLIENT_PREMATURE_DISCONNECTION_MESSAGE = Colors.colored_string("Client prematurely disconnected", Colors.WARNING)
    FAILED_CONNECTION_MESSAGE = Colors.colored_string("Player {number} failed to connect properly. Aborting game.", Colors.WARNING)
    CLIENT_BAD_NAME_MESSAGE = Colors.colored_string("Player {number} name is invalid. Aborting game.", Colors.WARNING)

    def __init__(self, ip, tcp_port, udp_port):
        self.tcp_port = tcp_port
        self.ip = ip
        self.question_generator = rqg.RandomQuestionGenerator()
        self.WINNER = None
        self.WAITING_FOR_PLAYERS = True
        self.broadcasting_socket = socket(AF_INET, SOCK_DGRAM)
        self.broadcasting_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((ip, tcp_port))
        self.server_socket.listen(self.PLAYERS_COUNT)
        self.stat = Statistics()
        print(self.SERVER_START_MESSAGE)

    def close_server(self):
        self.server_socket.close()
        self.broadcasting_socket.close()

    def run(self):
        try:
            broadcasting_thread = Thread(target = self.send_out_offers, args = ())
            broadcasting_thread.setDaemon(True)
            broadcasting_thread.start()
            while 1:
                # wait for 2 players to connect
                self.WAITING_FOR_PLAYERS = True
                players_conections = self.listen()

                # wait 10 seconds
                time.sleep(5)

                # begin the game
                self.game_mode(players_conections)

                # close connections with players
                players_conections[0].close()
                players_conections[1].close()
                print(self.GAME_OVER_MESSAGE)
        except KeyboardInterrupt:
            self.close_server()

    def send_out_offers(self):
        while True:
            if self.WAITING_FOR_PLAYERS is True:
                self.broadcasting_socket.sendto(pack(self.PACKING_FORMAT, self.MAGIC_COOKIE, self.MESSAGE_TYPE, self.tcp_port),
                                                (self.BROADCAST_DEST_IP, self.BROADCAST_DEST_PORT))
                time.sleep(self.BROADCAST_TIME_INTERVAL)
            else:
                time.sleep(1)

    def listen(self):
        players_conections = [None, None]
        connected_players = 0
        while connected_players < self.PLAYERS_COUNT:
            connection, _ = self.server_socket.accept()
            players_conections[connected_players] = connection
            if(players_conections[connected_players] != None):
                connected_players += 1
        self.WAITING_FOR_PLAYERS = False
        return players_conections

    def listen_to_player(self, player_sock, message, answer, player_name, other_player_name ,game_over):
        self.send_string_message(player_sock, message)
        player_answer = self.receive_string_message(player_sock, self.ANSWER_SIZE, self.GAME_DURATION)
        self.stat.add_key(player_answer)
        if player_answer != None and self.WINNER == None:
            if player_answer == answer:
                self.WINNER = player_name
            elif self.WINNER == None:
                self.WINNER = other_player_name
        game_over.set()

    def game_mode(self, players_conections):
        self.WINNER = None
        player0_sock = players_conections[0]
        player1_sock = players_conections[1]

        # getting the names of the 2 players
        players_names = self.get_players_names(player0_sock, player1_sock)
        if players_names == None:
            return

        (question, answer) = self.question_generator.generate_random_math_question()
        message = self.GAME_WELCOME_MESSAGE.format(**{"name0": players_names[0], "name1": players_names[1], "question": question})

        self.stat.add_pair(players_names[0].replace('\n', ''),players_names[1].replace('\n', ''))
        # actually perform the game
        game_over = threading.Event()
        thread0 = Thread(target = self.listen_to_player, args = (player0_sock, message, answer, players_names[0], players_names[1], game_over))
        thread1 = Thread(target = self.listen_to_player, args = (player1_sock, message, answer, players_names[1], players_names[0], game_over))
        thread0.start()
        thread1.start()
        
        # main thread waits for the game to end
        game_over.wait(self.GAME_DURATION)

        self.announce_results(answer, player0_sock, player1_sock)

    def announce_results(self, answer, player0_sock, player1_sock):
        if self.WINNER != None:
            message = self.GAME_END_WINNER_MESSAGE.format(**{"answer": answer, "winner": self.WINNER})
            self.stat.add_group_win(self.WINNER.replace('\n', ''))
        else:
            message = self.GAME_END_DRAW_MESSAGE.format(**{"answer": answer})
        message = message + self.stat.get_statistics()
        self.send_string_message(player0_sock, message)
        self.send_string_message(player1_sock, message)

    def get_players_names(self, player0_sock, player1_sock):
        player0_name = self.receive_string_message(player0_sock, 256, self.WAITING_FOR_NAME_TIME)
        player1_name = self.receive_string_message(player1_sock, 256, self.WAITING_FOR_NAME_TIME)

        # check for errors in client sent data
        if player0_name == None:
            print(self.FAILED_CONNECTION_MESSAGE.format(**{"number": 0}))
            return None
        if player1_name == None:
            print(self.FAILED_CONNECTION_MESSAGE.format(**{"number": 1}))
            return None
        if player0_name[len(player0_name) - 1] != self.END_OF_NAME:
            print(self.CLIENT_BAD_NAME_MESSAGE.format(**{"number": 0}))
            return None
        if player1_name[len(player1_name) - 1] != self.END_OF_NAME:
            print(self.CLIENT_BAD_NAME_MESSAGE.format(**{"number": 1}))
            return None

        return (player0_name, player1_name)

    def send_string_message(self, socket, message, encoding=ENCODING):
        try:
            socket.send(message.encode(encoding))
        except error:
            print(self.CLIENT_PREMATURE_DISCONNECTION_MESSAGE)

    def receive_string_message(self, socket, size, timeout=None, encoding=ENCODING):
        if timeout != None:
            socket.settimeout(timeout)
        try:
            bytes = socket.recv(size)
            return bytes.decode(encoding)
        except error:
            return None
        

def main():
    ip = sp.get_if_addr(Server.DEV_NETWORK)
    server = Server(ip, 6666, 7777)
    server.run()

if __name__ == "__main__":
    main()
