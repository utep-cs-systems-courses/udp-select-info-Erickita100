import socket
import os

seperator = ";"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

#set host and port
serverAddr = ('127.0.0.1', 50000)     

# the name of file we want to send, make sure it exists
filename = "Data.txt"
# get the file size
filesize = os.path.getsize(filename)

# create the client socket
s = socket.socket()

print("Connecting to: %s" % repr(serverAddr))
s.connect(serverAddr)
print("Connected.")

header =  filename + seperator + str(filesize)
# send the filename and filesize
s.send(header.encode())


# start sending the file
with open(filename, "rb") as f:
    while True:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # we use sendall to assure transimission in 
        # busy networks
        s.sendall(bytes_read)
        
print("File Transfer Complete.")   
        
# close the socket
s.close()


