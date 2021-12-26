import numpy as np
import time
import random
from socket import *
from threading import *
import scapy as sp


class Server:
    DEV_NETWORK = 'eth1'
    TEST_NETWORK = 'eth2'
    BROADCAST_DEST_PORT = 13117
    MAGIC_COOKIE = 0xabcddcba
    MESSAGE_TYPE = 0X2
    GAME_WELCOME_MESSAGE = "Welcome to Quick Maths.\nPlayer 1: {name0}\nPlayer 2: {name1}\n==\nPlease answer the following question as fast as you can:\n{question}"
    GAME_END_WINNER_MESSAGE = "Game over!\nThe correct answer was {answer}!\nCongratulations to the winner: {winner}"
    GAME_END_DRAW_MESSAGE = "Game over!\nThe correct answer was {answer}!\nWe have a draw!"
    GAME_OVER_MESSAGE = "Game over, sending out offer requests..."
    FAILED_CONNECTION_MESSAGE = "Player {number} failed to connect properly. Aborting game."
    ANSWER_SIZE = 1 # byte
    GAME_DURATION = 10  # seconds
    WINNER = None
    WAITING_FOR_PLAYERS = true

    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.question_generator = RandomQuestionGenerator()
        self.broadcasting_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(2)
        print(Colors.colored_string("Server started, listening on IP address " + ip, Colors.HEADER))

    def run():
        broadcasting_thread = Thread(send_out_offers, ())
        broadcasting_thread.setDaemon(True)
        broadcasting_thread.start()
        while 1:
            # wait for 2 players to connect
            WAITING_FOR_PLAYERS = true
            players_conections = listen()

            # wait 10 seconds
            time.sleep(10)

            # begin the game
            game_mode(players_conections)

            # close connections with players
            players_conections[0].close()
            players_conections[1].close()
            print(Colors.colored_string(GAME_OVER_MESSAGE, Colors.OKBLUE))

    def send_out_offers():
        while 1:
            if WAITING_FOR_PLAYERS is true:
                broadcasting_socket.sendto(pack(MAGIC_COOKIE, MESSAGE_TYPE, port), ('<broadcast>', BROADCAST_DEST_PORT))
            else:
                time.sleep(1)

    def listen():
        players_conections = [None, None]
        connected_players = 0
        while connected_players < 2:
            players_conections[connected_players] = server_socket.accept()[0]
            if(players_conections[connected_players] != None):
                connected_players += 1
        WAITING_FOR_PLAYERS = false
        return players_conections

    def listen_to_player(player_sock, message, answer, player_name, other_player_name ,game_over):
        player_sock.send(message)
        player_sock.settimeout(GAME_DURATION)
        player_answer = player_sock.recv(ANSWER_SIZE)
        if player_answer != None:
            if player_answer == answer:
                WINNER = player_name
            elif WINNER :
                WINNER = other_player_name
        game_over.set()

    def game_mode(players_conections):
        WINNER = None
        player0_sock = players_conections[0]
        player1_Sock = players_conections[1]

        # getting the names of the 2 players
        (player0_name, player1_name) = get_players_names(player0_sock, player1_sock)
        if (player0_name, player1_name) == None:
            return

        (question, answer) = question_generator.generate_random_math_question()
        message = GAME_WELCOME_MESSAGE.format(**{"name0": player0_name, "name1": player1_name, "question": question})
        message = Colors.colored_string(message, Colors.OKBLUE) + Colors.colored_string(question, Colors.OKGREEN)

        # actually perform the game
        game_over = threading.Event()
        thread0 = Thread(listen_to_player, (player0_sock, message, answer, player0_name, player1_name))
        thread1 = Thread(listen_to_player, (player1_sock, message, answer, player1_name, player0_name))
        thread0.start()
        thread1.start()
        
        # main thread waits for the game to end
        game_over.wait(GAME_DURATION)

        announce_results(answer)

    def announce_results(answer):
        if WINNER != None:
            message = GAME_END_WINNER_MESSAGE.format(**{"answer": answer, "winner": WINNER})
        else:
            message = GAME_END_DRAW_MESSAGE.format(**{"answer": answer})
        message = Colors.colored_string(message, Colors.OKCYAN)

        player0_sock.send(message)
        player1_sock.send(message)

    def get_players_names(player0_sock, player1_sock):
        player0_sock.settimeout(10)
        player0_name = player0_sock.recv(512)
        player1_sock.settimeout(0.5)
        player1_name = player1_sock.recv(512)

        if(player0_name == None):
            print(Colors.colored_string(FAILED_CONNECTION_MESSAGE.format(**{"number": 0}), Colors.WARNING))
            return None
        if(player1_name == None):
            print(Colors.colored_string(FAILED_CONNECTION_MESSAGE.format(**{"number": 1}), Colors.WARNING))
            return None

        return (player0_name, player1_name)
        

def main():
    port = 13117
    ip = sp.get_if_addr(DEV_NETWORK)
    server = Server(port, ip)
    server.run()

   

if __name__ == "__main__":
    main()
