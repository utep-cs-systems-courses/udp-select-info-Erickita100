import socket
import os


''' TODO:
send ack messages
split into byte segments
create a timeout if not arrived
resend after timeout

'''

# default params
serverAddr = ("", 50000)        # (ip address, port#) where "" represents "any" 

# receive 4096 bytes each time
BUFFER_SIZE = 20
seperator = ";"
ACK_TEXT = 'packet_received:'

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
header = client_socket.recv(BUFFER_SIZE).decode()

filesize, filename, numOfPackets = header.split(seperator)
# remove absolute path if there is
filename = os.path.basename(filename)

#adds a 1 to filename to distinguish file transfered
filename, format = filename.split(".");
filename = filename+ "1."+format

# convert to integer
filesize = int(filesize)
numOfPackets = int(numOfPackets)

# now time to send the acknowledgement
# encode the acknowledgement text
encodedAckText = bytes(ACK_TEXT+str(0), 'utf-8')
# send the encoded acknowledgement text
client_socket.sendall(encodedAckText)

# start receiving the file from the socket
# and writing to the file stream
with open(filename, "wb") as f:
    counter = 1
    while True:
        ACK_TEXT = 'packet_received:'
        # read 1024 bytes from the socket (receive)
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:    
            # nothing is received
            # file transmitting is done
            break
        # write to the file the bytes we just received
        f.write(bytes_read)
        
        # now time to send the acknowledgement for each packet
        # encode the acknowledgement text
        encodedAckText = bytes(ACK_TEXT+ str(counter), 'utf-8')
        # send the encoded acknowledgement text
        client_socket.sendall(encodedAckText)
        print("send ack to packet:", counter)
        counter = counter+1
        
print("File Transfer Complete.")        
# close the client socket
client_socket.close()
# close the server socket
s.close()

