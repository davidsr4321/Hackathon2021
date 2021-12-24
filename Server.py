import numpy as np
import time
import random
import socket
import threading
import ipaddress
import scipy.optimize as opt


class Server:
    GAME_WELCOME_MESSAGE = "Welcome to Quick Maths.\nPlayer 1: {name0}\nPlayer 2: {name1}\n==\nPlease answer the following question as fast as you can:\n"
    GAME_END_WINNER_MESSAGE = "Game over!\nThe correct answer was {answer}!\nCongratulations to the winner: {winner}"
    GAME_END_DRAW_MESSAGE = "Game over!\nThe correct answer was {answer}!\nWe have a draw!"
    winner = None

    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.server_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(2)
        print(Colors.colored_string("Server started, listening on IP address " + ip, Colors.HEADER))

    def start():
        while 1:
            # wait for 2 players to connect
            players_conections = listen()

            # wait 10 seconds
            t_end = time.time() + 60 * 10
            while time.time() < t_end:
                pass

            # begin the game
            game_mode(players_conections)

            # close connections with players
            players_conections[0].close()
            players_conections[1].close()
            print("Game over, sending out offer requests...")

    def send_out_offers():
        pass

    def listen():
        players_conections = [None, None]
        connected_players = 0
        while connected_players < 2:
            send_out_offers()
            server_socket.settimeout(60)
            players_conections[connected_players] = server_socket.accept()[0]
            if(players_conections[connected_players] != None) connected_players += 1
        return players_conections

    def generate_random_math_question():
        pass

    def listen_to_player(player_sock, message, answer, player_name, other_player_name):
        player_sock.send(message)
        t_end = time.time() + 60 * 10
        while time.time() < t_end:
            global winner
            player_answer = player_sock.recv(128)
            if player_answer == answer:
                winner = player_name
                break
            else:
                winner = other_player_name
                break
            if winner != None:
                break

    def game_mode(players_conections):
        winner = None
        player0_sock = players_conections[0]
        player1_Sock = players_conections[1]

        # getting the names of the 2 players
        player0_name = player0_sock.recv(512)
        player1_name = player1_Sock.recv(512)

        message = GAME_WELCOME_MESSAGE.format(**{"name0": player0_name, "name1": player1_name})
        (question, answer) = generate_random_math_question()
        message = Colors.colored_string(message, Colors.OKBLUE) + Colors.colored_string(question, Colors.OKGREEN)

        # actually perform the game
        thread0 = threading.Thread(listen_to_player, (player0_sock, message, answer, player0_name, player1_name))
        thread1 = threading.Thread(listen_to_player, (player1_sock, message, answer, player1_name, player0_name))
        thread0.start()
        thread1.start()
        thread0.join()
        thread1.join()

        # announce the results
        if winner != None:
            message = GAME_END_WINNER_MESSAGE.format(**{"answer": answer, "winner": winner})
        else:
            message = GAME_END_DRAW_MESSAGE.format(**{"answer": answer})
        message = Colors.colored_string(message, Colors.OKCYAN)

        player0_sock.send(message)
        player1_sock.send(message)

        

def main():
    port = 13117
    ip = ipaddress.ip_address(u'172.0.0.1') #fix ip address
    server = Server(port, ip)
    server.start()

   

if __name__ == "__main__":
    main()
