import socket

def client(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message.encode('utf-8'))
        s.shutdown(socket.SHUT_WR)  # Shutting down the sending side
        response = s.recv(1024)
        print('Received from server:', response.decode('utf-8'))

client('localhost', 1998, "Hello, Server!")
