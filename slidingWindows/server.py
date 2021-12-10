import sys
from socket import *
from select import select
import os
import time

upperServerAddr = ("", 50001)   # any addr, port 50,000

# receive 4096 bytes each time
BUFFER_SIZE = 256
seperator = ";"
ACK_TEXT = 'packet_received:'
filename = " " 
clientAddrPort = " "
counter = 0
WINDOW_SIZE = 3
win = []
numOfPackets = 0
lastpacket = 1
def receiveHeader(sock):
   header,clientAddrPort = sock.recvfrom(BUFFER_SIZE)
   header = header.decode()
   global filename
   global counter
   global  numOfPackets
   filesize, filename = header.split(seperator,1)
   # remove absolute path if there is
   filename = os.path.basename(filename)
   #adds a 1 to filename to distinguish file transfered
   filename, format = filename.split(".");
   filename = filename+ "1."+format
   # convert to integer
   filesize = int(filesize)
   # now time to send the acknowledgement
   # encode the acknowledgement text
   encodedAckText = str(ACK_TEXT+str(counter))
   # send the encoded acknowledgement text
   sock.sendto(encodedAckText.encode(),clientAddrPort)
   print("send ack to header packet:", counter)
   readSockFunc[upperServerSocket] = receiveFile

def receiveFile(sock):
   global win
   global WINDOW_SIZE
   global lastpacket
   # start receiving the file from the socket
   # and writing to the file stream
   with open(filename, "ab") as f:
       
        # read 1024 bytes from the socket (receive)
       message, clientAddrPort = sock.recvfrom(BUFFER_SIZE+5)
       payloadNum, bytes_read = message.split(seperator,1)
       if not bytes_read:    
            # nothing is received
           return False
            # write to the file the bytes we just received
            
       if int(lastpacket) == int(payloadNum):
          f.write(bytes_read)
          f.close()
          lastpacket = lastpacket+1
       win.append(int(payloadNum))
       if len(win) == WINDOW_SIZE or numOfPackets in win :
            sendAcks(sock,clientAddrPort,win)
            win = []
       
def sendAcks(sock, clientAddrPort,win):
	global WINDOW_SIZE
	ACK_TEXT = 'packet_received:'
	for i in win:
         encodedAckText = str(ACK_TEXT+ str(i))
         # send the encoded acknowledgement text
         sock.sendto(encodedAckText,clientAddrPort)
         print("send ack to packet:",encodedAckText )

       


upperServerSocket = socket(AF_INET, SOCK_DGRAM)
upperServerSocket.bind(upperServerAddr)
upperServerSocket.setblocking(False)

 # map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}              # broken

timeout = 0.2                     # select delay before giving up, in seconds

 # function to call when upperServerSocket is ready for reading
readSockFunc[upperServerSocket] = receiveHeader

print("ready to receive")
while 1:
   readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                 list(writeSockFunc.keys()), 
                                                 list(errorSockFunc.keys()),
                                                 timeout)
   if not readRdySet and not writeRdySet and not errorRdySet:
     print("timeout: no events")
   for sock in readRdySet:
     readSockFunc[sock](sock)
