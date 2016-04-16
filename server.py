import socket
import commandhandler


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('192.168.0.3', 10000)
print 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print 'waiting for a connection'
    connection, client_address = sock.accept()
    print 'connection from', client_address

    # Receive the data in small chunks and retransmit it
    while True:
        data = connection.recv(1024)
        print 'received "%s"' % data
        if data:
            print data
            commandhandler.handle_command(data)

sock.close()
