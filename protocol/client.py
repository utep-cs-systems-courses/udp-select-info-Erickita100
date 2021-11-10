from socket import *
import sys, re   
import os     
from time import time

seperator = ";"
BUFFER_SIZE = 20 # send 4096 bytes each time step
ACK_TEXT = 'packet_received:'
 # default params
serverAddr = ('localhost', 50000)       

                         
# the name of file we want to send, make sure it exists
filename = "Data.txt"
# get the file size
filesize = os.path.getsize(filename)
 
 #get number of packets, 8 bytes each
numOfPackets = int(filesize/BUFFER_SIZE)


def usage():
     print("usage: %s [--serverAddr host:port]"  % sys.argv[0])
     sys.exit(1)

try:
     args = sys.argv[1:]
     while args:
         sw = args[0]; del args[0]
         if sw in ("--serverAddr", "-s"):
             addr, port = re.split(":", args[0]); del args[0]
             serverAddr = (addr, int(port)) # addr can be a string (yippie)
         else:
             print("unexpected parameter %s" % args[0])
             usage();
except:
     usage()


print("Connecting to serverAddr = %s" % repr(serverAddr))

header =  str(filesize) + seperator + filename + seperator + str(numOfPackets)


clientSocket = socket(AF_INET, SOCK_DGRAM)

clientSocket.sendto(header.encode(), serverAddr)
#modifiedMessage, serverAddrPort = clientSocket.recvfrom(2048)
#print('Modified message from %s is "%s"' % (repr(serverAddrPort), modifiedMessage.decode()))

encodedAckText, serverAddrPort  = clientSocket.recvfrom(BUFFER_SIZE)
ackText = encodedAckText.decode('utf-8')

# log if acknowledgment was successful
if ackText == (ACK_TEXT+str(0)):
   print('server acknowledged reception of packet:'+str(0))
else:
   print('error: server has sent back ' + ackText)
   
# start sending the file
with open(filename, "rb") as f:
    counter = 1
    attempts = 1
    RTT = 0
    while attempts<3:
        
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # we use sendall to assure transimission in 
        # busy networks
        start = time()
        payload = str(counter) +seperator +bytes_read
        clientSocket.sendto(payload,serverAddr)
        
        encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
        ackText = encodedAckText.decode('utf-8')
        
        
        received = True
        while received:
          # log if acknowledgment was successful
          if ackText == (ACK_TEXT+str(counter)):
             print('server acknowledged reception of packet:'+str(counter))
             
             RTT = time() - start
             print('RTT= '+str(RTT))
             received = False
          else:
             print('error: server has not sent back packet:' + str(counter))
             if (attempts>=3):
             	print('Number of attempts succeeded, end connection')
             	break
             else: 
                print('Re-sending packet:' + str(counter))
                clientSocket.sendto(bytes_read,serverAddr)
                encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
                ackText = encodedAckText.decode('utf-8')
                attempts= attempts + 1
        counter = counter+1
   
     
print("File Transfer Complete.")   
        
# close the socket
clientSocket.close()   
