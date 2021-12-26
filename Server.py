import threading
import time
from struct import *
from socket import *
from threading import *
import scapy.all as sp
import RandomQuestionGenerator
import Colors

class Server:
    DEV_NETWORK = 'eth1'
    TEST_NETWORK = 'eth2'
    BROADCAST_DEST_PORT = 13117
    MAGIC_COOKIE = 0xabcddcba
    MESSAGE_TYPE = 0X2
    PLAYERS_COUNT = 2
    ANSWER_SIZE = 1 # byte
    GAME_DURATION = 10  # seconds
    SERVER_START_MESSAGE = "Server started, listening on IP address "
    GAME_WELCOME_MESSAGE = "Welcome to Quick Maths.\nPlayer 1: {name0}\nPlayer 2: {name1}\n==\nPlease answer the following question as fast as you can:\n{question}"
    GAME_END_WINNER_MESSAGE = "Game over!\nThe correct answer was {answer}!\nCongratulations to the winner: {winner}"
    GAME_END_DRAW_MESSAGE = "Game over!\nThe correct answer was {answer}!\nWe have a draw!"
    GAME_OVER_MESSAGE = "Game over, sending out offer requests..."
    FAILED_CONNECTION_MESSAGE = "Player {number} failed to connect properly. Aborting game."

    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.question_generator = RandomQuestionGenerator()
        self.WINNER = None
        self.WAITING_FOR_PLAYERS = True
        self.broadcasting_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(2)
        print(Colors.colored_string(self.SERVER_START_MESSAGE + ip, Colors.HEADER))

    def run(self):
        broadcasting_thread = Thread(self.send_out_offers, ())
        broadcasting_thread.setDaemon(True)
        broadcasting_thread.start()
        while 1:
            # wait for 2 players to connect
            self.WAITING_FOR_PLAYERS = True
            players_conections = self.listen()

            # wait 10 seconds
            time.sleep(10)

            # begin the game
            self.game_mode(players_conections)

            # close connections with players
            players_conections[0].close()
            players_conections[1].close()
            print(Colors.colored_string(self.GAME_OVER_MESSAGE, Colors.OKBLUE))

    def send_out_offers(self):
        while True:
            if self.WAITING_FOR_PLAYERS is True:
                self.broadcasting_socket.sendto(pack('IbH', self.MAGIC_COOKIE, self.MESSAGE_TYPE, self.port), ('<broadcast>', self.BROADCAST_DEST_PORT))
            else:
                time.sleep(1)

    def listen(self):
        players_conections = [None, None]
        connected_players = 0
        while connected_players < self.PLAYERS_COUNT:
            players_conections[connected_players] = self.server_socket.accept()[0]
            if(players_conections[connected_players] != None):
                connected_players += 1
        self.WAITING_FOR_PLAYERS = False
        return players_conections

    def listen_to_player(self, player_sock, message, answer, player_name, other_player_name ,game_over):
        self.send_string_message(player_sock, message)
        player_sock.settimeout(self.GAME_DURATION)
        player_answer = self.receive_string_message(player_sock, self.ANSWER_SIZE)
        if player_answer != None:
            if player_answer == answer:
                self.WINNER = player_name
            elif self.WINNER :
                self.WINNER = other_player_name
        game_over.set()

    def game_mode(self, players_conections):
        self.WINNER = None
        player0_sock = players_conections[0]
        player1_sock = players_conections[1]

        # getting the names of the 2 players
        (player0_name, player1_name) = self.get_players_names(player0_sock, player1_sock)
        if (player0_name, player1_name) == None:
            return

        (question, answer) = self.question_generator.generate_random_math_question()
        message = self.GAME_WELCOME_MESSAGE.format(**{"name0": player0_name, "name1": player1_name, "question": question})
        message = Colors.colored_string(message, Colors.OKBLUE) + Colors.colored_string(question, Colors.OKGREEN)

        # actually perform the game
        game_over = threading.Event()
        thread0 = Thread(self.listen_to_player, (player0_sock, message, answer, player0_name, player1_name))
        thread1 = Thread(self.listen_to_player, (player1_sock, message, answer, player1_name, player0_name))
        thread0.start()
        thread1.start()
        
        # main thread waits for the game to end
        game_over.wait(self.GAME_DURATION)

        self.announce_results(answer, player0_sock, player1_sock)

    def announce_results(self, answer, player0_sock, player1_sock):
        if self.WINNER != None:
            message = self.GAME_END_WINNER_MESSAGE.format(**{"answer": answer, "winner": self.WINNER})
        else:
            message = self.GAME_END_DRAW_MESSAGE.format(**{"answer": answer})
        message = Colors.colored_string(message, Colors.OKCYAN)

        self.send_string_message(player0_sock, message)
        self.send_string_message(player1_sock, message)

    def get_players_names(self, player0_sock, player1_sock):
        player0_sock.settimeout(10)
        player0_name = self.receive_string_message(player0_sock, 256)
        player1_sock.settimeout(0.5)
        player1_name = self.receive_string_message(player1_sock, 256)

        if(player0_name == None):
            print(Colors.colored_string(self.FAILED_CONNECTION_MESSAGE.format(**{"number": 0}), Colors.WARNING))
            return None
        if(player1_name == None):
            print(Colors.colored_string(self.FAILED_CONNECTION_MESSAGE.format(**{"number": 1}), Colors.WARNING))
            return None

        return (player0_name, player1_name)

    def send_string_message(self, socket, message, encoding='utf8'):
        socket.send(message.encode(encoding))

    def receive_string_message(self, socket, size, encoding='utf8'):
        bytes = socket.recv(size)
        return bytes.decode(encoding)
        

def main():
    port = 13117
    ip = sp.get_if_addr(Server.DEV_NETWORK)
    server = Server(port, ip)
    server.run()

   

if __name__ == "__main__":
    main()
