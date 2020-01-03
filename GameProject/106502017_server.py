import socket
import threading
import pickle
from queue import Queue

message_queue = Queue()
status = None
ADDRESS = ('127.0.0.1', 12801)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDRESS)
server_socket.listen(5)

def main():
    players = []
    print('waiting for connect...')
    while len(players) < 2:
        (client_socket, address) = server_socket.accept()
        print('clinet:', client_socket, 'address:', address)
        # connect successly
        msg = client_socket.recv(4096)
        print(msg)
        if msg == b'join_game':
            players.append(client_socket)
            data = (len(players), True)
            players[0].send(pickle.dumps(data))
            if (len(players) == 2):
                data = (len(players), False)
                players[1].send(pickle.dumps(data))
            threading.Thread(target=receive_message, args=(client_socket,)).start()
    # send data to all clients
    while True:
        job = message_queue.get()
        for player in players:
            player.send(pickle.dumps(job))
    server_socket.close()


def receive_message(client_socket):
    # receive data from clients
    while True:
        data = client_socket.recv(4096)
        data_arr = pickle.loads(data)
        if data_arr == b'':
            break
        message_queue.put(data_arr)

main()