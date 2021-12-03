from socket import *
import sys, re   
import os     
from time import time
from select import select
import socket


seperator = ";"
BUFFER_SIZE = 256 # send 256 bytes each time step
ACK_TEXT = 'packet_received:'
 # default params
serverAddr = ('localhost', 50000)       
filename = "Data.txt"
counter = 1
numOfPackets = 0

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
    global numOfPackets
    # get the file size
    filesize = os.path.getsize(filename)
 
    #get number of packets, bytes each
    numOfPackets = int(filesize/BUFFER_SIZE)+1
    
    header =  str(filesize) + seperator + filename
    clientSocket.sendto(header.encode(), serverAddr)
    received = False
    attempts = 1
    while not received:
         try:
            encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
            ackText = encodedAckText.decode('utf-8')
            # log if acknowledgment was successful
            if ackText == (ACK_TEXT+str(0)):
              print('server acknowledged reception of header:'+str(0))
              received = True
              sendFile(clientSocket)
           
         except socket.timeout:
             print('error: server has not sent back ' + ackText)
             if (attempts <3):
                print('resending header')
                clientSocket.sendto(header.encode(),serverAddr)
                attempts = attempts+1
             else:
                print("server didnt respond, goodbye")
                sys.exit()
       
def sendFile(sock):
        # start sending the file
    global filename
    print("sending file...")
    counter = 1
    RTTTime = 0
    file = open(filename, "rb")
    complete = False
    while True:
       #global counter
       attempts = 1
       RTT = 0
       # read the bytes from the file
       bytes_read = file.read(BUFFER_SIZE)
       if not bytes_read:
            # file transmitting is done
               break
           #send packet and record time
       start = time()
       payload = str(counter) +seperator +bytes_read
       clientSocket.sendto(payload,serverAddr)
           #check for ack received
       received = False
       attempts =1
       #counter = counter +1
       while not received:
          try:
             #receive acks for sliding wind
             encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
             ackText = encodedAckText.decode('utf-8')
           
               # log if acknowledgment was successful
             if ackText == (ACK_TEXT+str(counter)):
                 print('server acknowledged reception of packet:'+str(counter))
                 RTT = (time() - start) *1000
                 print('RTT= '+str(RTT))
                 received = True
                 if(counter == numOfPackets):
                 	complete = True
                 	print("File Transfer Complete.")
                 	sys.exit(1)
          except socket.timeout:
                 #resend packets
                 print('error: server has not sent back packet:' + str(counter))
                 if (attempts>3):
             	   print('Number of attempts succeeded, end connection')
             	   sys.exit(1)
                 else: 
                   print('Re-sending packet:' + str(counter))
                   clientSocket.sendto(payload,serverAddr)
                   attempts= attempts + 1

       counter = counter +1
    file.close()

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

clientSocket = socket.socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(2)
#clientSocket.setblocking(False)

 # map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}              # broken

timeout = 2                     # select delay before giving up, in seconds

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
