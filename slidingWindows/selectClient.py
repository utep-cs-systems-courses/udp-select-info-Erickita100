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
WINDOW_SIZE = 3
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
      attempts = 1
      print("sending header..")
      global BUFFER_SIZE
	  # the name of file we want to send, make sure it exists
      global filename
      global numOfPackets
      ackText=""
      # get the file size
      filesize = os.path.getsize(filename)
 
      #get number of packets, bytes each
      numOfPackets = int(filesize/BUFFER_SIZE)+1
    
      header =  str(filesize) + seperator + filename
      clientSocket.sendto(header.encode(), serverAddr)
      received = False
      while not received:
         try:
            encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
            ackText = encodedAckText.decode('utf-8')
            # log if acknowledgment was successful
            if ackText == (ACK_TEXT+str(0)):
              print('server acknowledged reception of packet:'+str(0))
              received = True
              sendFile(clientSocket)
           
         except socket.timeout:
             print('error: server has not sent back header' + ackText)
             if (attempts <3):
                print("Resending header")
                clientSocket.sendto(header.encode(),serverAddr)
                attempts = attempts+1
             else:
                print("server didnt respond, goodbye")
                sys.exit()
       
def sendFile(sock):
        # start sending the file
    global filename
    global WINDOW_SIZE
    print("sending file...")
    counter = 1
    RTTTimes = {}
    file = open(filename, "rb")
    attempts = 1
    complete = False
    win = {}
    sent = []
    while True:
       #global counter
       RTT = 0
       attempts =1
       #win = {}
       while len(win) < WINDOW_SIZE and attempts<3:
           # read the bytes from the file
           bytes_read = file.read(BUFFER_SIZE)
           if not bytes_read:
            # file transmitting is done
               break
           #send packet and record time
           win[counter]= bytes_read
           counter = counter +1
           
           
       #print("Window:",sorted(win.keys()))
       for key in sorted(win.keys()):
           if key not in sent:
              RTTTimes[key]=time()
              payload = str(key) +seperator +win[key]
              print("sending packet: "+str(key))
              clientSocket.sendto(payload,serverAddr)
              sent.append(key)
           #counter = counter +1
       #for key in sorted(win.keys()):
            #receive acks for sliding window
       print("Window:",sorted(win.keys()))
       current = list(sorted(win.keys()))[0]
       received = False
      
       while not received:
              try:
                 encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
                 ackText = encodedAckText.decode('utf-8')
                 # log if acknowledgment was successful
                 if ackText == (ACK_TEXT+str(current)):
                    print('server acknowledged reception of packet:'+str(current))
                    received = True
                    win.pop(current)
                    RTT = (time() - RTTTimes[current]) *1000
                    print('RTT= '+str(RTT))
                    if(current == numOfPackets):
                 	   print("File Transfer Complete.")
                 	   sys.exit(1)
                 	
              except socket.timeout:
                 #resend packets
                 if (attempts>3):
             	   print('Number of attempts succeeded, end connection, goodbye')
             	   sys.exit(1)
                 else: 
                   print('Re-sending packet:' + str(current))
                   payload = str(current)+seperator+win[current]
                   clientSocket.sendto(payload,serverAddr)
                   attempts= attempts + 1


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
clientSocket.settimeout(0.2)
#clientSocket.setblocking(False)

 # map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}              # broken

#timeout = 1                     # select delay before giving up, in seconds

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
