from socket import *
import sys, re   
import os     
from time import time
from select import select



seperator = ";"
BUFFER_SIZE = 256 # send 256 bytes each time step
ACK_TEXT = 'packet_received:'
 # default params
serverAddr = ('localhost', 50000)       
filename = "Data.txt"
counter = 1
WINDOW_SIZE = 3

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
 
    #get number of packets, bytes each
    numOfPackets = int(filesize/BUFFER_SIZE)
    header =  str(filesize) + seperator + filename + seperator + str(numOfPackets)
    clientSocket.sendto(header.encode(), serverAddr)
       
def sendFile(sock):
        # start sending the file
    global filename
    global WINDOW_SIZE
    print("sending file...")
    counter = 1
    RTTTimes = {}
    file = open(filename, "rb")
    byte = True
    while byte:
       #global counter
       attempts = 1
       RTT = 0
       packets = 0
       timeout = 5 
       win = {}
       while len(win) < WINDOW_SIZE and attempts<3:
           # read the bytes from the file
           bytes_read = file.read(BUFFER_SIZE)
           if not bytes_read:
            # file transmitting is done
               continue
           #send packet and record time
           win[counter]= bytes_read
           start = time()
           RTTTimes[counter]=start
           payload = str(counter) +seperator +bytes_read
           clientSocket.sendto(payload,serverAddr)
           #check for ack received
           #received = True
           counter = counter +1
       for key in win.keys():
            #receive acks for sliding wind
           encodedAckText, serverAddrPrt = clientSocket.recvfrom(BUFFER_SIZE)
           ackText = encodedAckText.decode('utf-8')
     
           
               # log if acknowledgment was successful
           if ackText == (ACK_TEXT+str(key)):
                 print('server acknowledged reception of packet:'+str(key))
                 win.pop(key)
                 RTT = (time() - RTTTimes[key]) *1000
                 print('RTT= '+str(RTT))
                 
           
           '''
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
'''
           #counter = counter+1
    if (attempts<3):     
       print("File Transfer Complete.") 
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
