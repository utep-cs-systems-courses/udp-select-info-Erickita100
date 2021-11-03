import socket
import os

seperator = ";"
BUFFER_SIZE = 20 # send 4096 bytes each time step
ACK_TEXT = 'packet_received:'

#set host and port
serverAddr = ('127.0.0.1', 50000)     

# the name of file we want to send, make sure it exists
filename = "Data.txt"
# get the file size
filesize = os.path.getsize(filename)
 
 #get number of packets, 8 bytes each
numOfPackets = int(filesize/BUFFER_SIZE)

# create the client socket
s = socket.socket()

print("Connecting to: %s" % repr(serverAddr))
s.connect(serverAddr)
print("Connected.")

header =  str(filesize) + seperator + filename + seperator + str(numOfPackets)

# send the filename and filesize
s.send(header.encode())

encodedAckText = s.recv(1024)
ackText = encodedAckText.decode('utf-8')

# log if acknowledgment was successful
if ackText == (ACK_TEXT+str(0)):
   print('server acknowledged reception of packet:'+str(0))
else:
   print('error: server has sent back ' + ackText)
   

# start sending the file
with open(filename, "rb") as f:
    counter = 1
    while True:
        
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # we use sendall to assure transimission in 
        # busy networks
        s.sendall(bytes_read)
        
        encodedAckText = s.recv(1024)
        ackText = encodedAckText.decode('utf-8')
        
        # log if acknowledgment was successful
        if ackText == (ACK_TEXT+str(counter)):
           print('server acknowledged reception of packet:'+str(counter))
        else:
           print('error: server has sent back packet:' + str(counter))
        counter = counter+1
        
print("File Transfer Complete.")   
        
# close the socket
s.close()


