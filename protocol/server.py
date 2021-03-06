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
numOfPackets = 0

def receiveHeader(sock):
   header,clientAddrPort = sock.recvfrom(BUFFER_SIZE)
   header = header.decode()
   global filename
   global counter
   filesize, filename = header.split(seperator)
   # remove absolute path if there is
   filename = os.path.basename(filename)
   #adds a 1 to filename to distinguish file transfered
   filename, format = filename.split(".");
   filename = filename+ "1."+format
   # convert to integer
   filesize = int(filesize)
   #numOfPackets = int(numOfPackets)
   # now time to send the acknowledgement
   # encode the acknowledgement text
   encodedAckText = str('packet_received:'+str(counter))
   # send the encoded acknowledgement text
   sock.sendto(encodedAckText.encode(),clientAddrPort)
   print("send ack to header packet:", counter)
   readSockFunc[upperServerSocket] = receiveFile
   #receiveFile(sock)

def receiveFile(sock):
   # start receiving the file from the socket
   # and writing to the file stream
   with open(filename, "ab") as f:
       
       #ACK_TEXT = 'packet_received:'
        # read 1024 bytes from the socket (receive)
       bytes_read, clientAddrPort = sock.recvfrom(BUFFER_SIZE)
       payloadNum, bytes_read = bytes_read.split(seperator)
       if (int(payloadNum)!=0):
            f.write(str(bytes_read))
            f.close()
       if not bytes_read:    
            # nothing is received
            # file transmitting is done
           return False
            # write to the file the bytes we just received
       sendAck(sock,clientAddrPort,payloadNum)
       
def sendAck(sock, clientAddrPort,num):
     ACK_TEXT = 'packet_received:'
     encodedAckText = str(ACK_TEXT+ str(num))
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

timeout = 5                     # select delay before giving up, in seconds

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
