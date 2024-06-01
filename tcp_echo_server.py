import socket
import select
from collections import defaultdict
import os

PORT = os.getenv('PORT', 3000)
BUFFER_SIZE_IN_BYTES = 1024

# create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# make server socket non blocking to allow concurrent connections
server_socket.setblocking(False)

# bind it to this machine's IP address and a random port number
host_ip_address = socket.gethostname()
server_address = (host_ip_address, PORT)
server_socket.bind(server_address)

# start listening
server_socket.listen(5)

# lists for select to watch
reads, writes = set([server_socket]), set([])

socket_to_buffer_map = defaultdict(list)
socket_to_response_map = defaultdict(list)

# handle recv and send
try:
    while True:

        ready_for_reads, ready_for_writes, _ = select.select(reads, writes, [])

        for sock in ready_for_reads:
            # we have to handle server sockets and client sockets differently
            # in server socket ready for read means new connection available
            if sock is server_socket:
                client_socket, client_address = sock.accept()
                reads.add(client_socket)
            else:
                data = sock.recv(1024)
                socket_to_buffer_map[sock].append(data)
                if not data:
                    socket_to_response_map[sock] = b''.join(socket_to_buffer_map[sock])
                    reads.remove(sock)
                    writes.add(sock)

        for sock in ready_for_writes:

            # NOTE: server socket will never be here
            remaining_data_to_send = socket_to_response_map[sock]
            if len(remaining_data_to_send) > 0:
                curr_sent_bytes = sock.send(remaining_data_to_send)
                socket_to_response_map[sock] = remaining_data_to_send[curr_sent_bytes:]
            else:
                writes.remove(sock)
                sock.close()

except Exception as E:
    print(E)
    server_socket.close()
        
