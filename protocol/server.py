#! /usr/bin/env python3
# udp demo -- simple select-driven uppercase server

# Eric Freudenthal with mods by Adrian Veliz

import sys
from socket import *
from select import select

serverAddr= ("", 50000)   # any addr, port 50,000


def welcome(sock):
  "run this function when sock has rec'd a message"
  message, clientAddrPort = sock.recvfrom(2048)
  print("from %s: rec'd '%s'" % (repr(clientAddrPort), message))
  modifiedMessage = "Hello Client";
  sock.sendto(modifiedMessage, clientAddrPort)

  
server = socket(AF_INET, SOCK_DGRAM)
server.bind(serverAddr)
server.setblocking(False)


# map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}              # broken

timeout = 5                     # select delay before giving up, in seconds

# function to call when upperServerSocket is ready for reading
readSockFunc[socket] = welcome


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

