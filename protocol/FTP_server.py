import socket
import os

# default params
serverAddr = ("", 50000)        # (ip address, port#) where "" represents "any" 

# receive 4096 bytes each time
BUFFER_SIZE = 4096
seperator = ";"

# create the server socket
# TCP socket
s = socket.socket()

# bind the socket to our local address
s.bind(serverAddr)


# enabling our server to accept connections
# 5 here is the number of unaccepted connections that
# the system will allow before refusing new connections
s.listen(5)

print("Listening...")

# accept connection if there is any
client_socket, address = s.accept() 
# if below code is executed, that means the sender is connected
print("%s is connected." % repr(address))


# receive the file infos
# receive using client socket, not server socket
received = client_socket.recv(BUFFER_SIZE).decode()
filename, filesize = received.split(seperator)
# remove absolute path if there is
filename = os.path.basename(filename)
filename, format = filename.split(".");
filename = filename+ "1."+format
# convert to integer
filesize = int(filesize)

# start receiving the file from the socket
# and writing to the file stream
with open(filename, "wb") as f:
    while True:
        # read 1024 bytes from the socket (receive)
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:    
            # nothing is received
            # file transmitting is done
            break
        # write to the file the bytes we just received
        f.write(bytes_read)
        
print("File Transfer Complete.")        
# close the client socket
client_socket.close()
# close the server socket
s.close()

