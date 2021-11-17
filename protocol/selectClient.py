from socket import *
import sys, re   
import os     
from time import time
from select import select



seperator = ";"
BUFFER_SIZE = 20 # send 4096 bytes each time step
ACK_TEXT = 'packet_received:'
 # default params
serverAddr = ('localhost', 50000)       
attempts = 0
filename = "Data.txt"
counter = 1

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
     
def sendHeader():
    print("sending header..")
    global BUFFER_SIZE
	# the name of file we want to send, make sure it exists
    global filename
    # get the file size
    filesize = os.path.getsize(filename)
 
    #get number of packets, 8 bytes each
    numOfPackets = int(filesize/BUFFER_SIZE)
    header =  str(filesize) + seperator + filename + seperator + str(numOfPackets)

    clientSocket.sendto(header.encode(), serverAddr)
       
def sendFile(sock):
        # start sending the file
    global filename
    print("sending file...")
    with open(filename, "rb") as f:
       global counter
       global attempts
       attempts = 1
       RTT = 0
       
       timeout = 5 
       while attempts<3:
           
           # read the bytes from the file
           bytes_read = f.read(BUFFER_SIZE)
           if not bytes_read:
            # file transmitting is done
               break
           #send packet and record time
           start = time()
           payload = str(counter) +seperator +bytes_read
           clientSocket.sendto(payload,serverAddr)
           #check for ack received
           received = True
           while received:
              #receive ack
              encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
              ackText = encodedAckText.decode('utf-8')
               # log if acknowledgment was successful
              if ackText == (ACK_TEXT+str(counter)):
                 print('server acknowledged reception of packet:'+str(counter))
             
                 RTT = (time() - start) *1000
                 print('RTT= '+str(RTT))
                 received = False
              else:
                 #resend packet
                 print('error: server has not sent back packet:' + str(counter))
                 if (attempts>=3):
             	   print('Number of attempts succeeded, end connection')
             	   break
                 else: 
                   print('Re-sending packet:' + str(counter))
                   clientSocket.sendto(bytes_read,serverAddr)
                   attempts= attempts + 1
           counter = counter+1
    if (attempts<3):     
       print("File Transfer Complete.") 
      
def recvAck(sock):
           encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
           ackText = encodedAckText.decode('utf-8')
           # log if acknowledgment was successful
           if ackText == (ACK_TEXT+str(0)):
              print('server acknowledged reception of packet:'+str(0))
              sendFile(sock)
           else:
              print('error: server has not sent back ' + ackText)
           
    

print("Connecting to serverAddr = %s" % repr(serverAddr))

clientSocket = socket(AF_INET, SOCK_DGRAM)
#clientSocket.setblocking(False)

 # map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}              # broken

timeout = 1                     # select delay before giving up, in seconds

 # function to call when upperServerSocket is ready for reading
readSockFunc[clientSocket] = recvAck

sendHeader()
while 1:
   readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                 list(writeSockFunc.keys()), 
                                                 list(errorSockFunc.keys()),
                                                 timeout)
   if not readRdySet and not writeRdySet and not errorRdySet:
     print("timeout: no events")
   for sock in readRdySet:
     readSockFunc[sock](sock)
