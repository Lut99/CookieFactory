# TCP TEST.py
#
# This script functions as a test for TCP sockets

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import socket
import struct
import time
import Interface

KEY = "9zTw%V'VLl%R0,@,4;IQ~(/@UDT*|=,3"


# Run the Connection Server on a separate thread
srv = Interface.ConnectionServer()
srv.start()

# Create a socket and connect to the local server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sock.connect(("localhost", 8080))

    # Send the password message
    # Make sure the opcode is 8 bit long
    opcode = struct.pack("!B", 0)
    # Compute the length of the message
    key = KEY.encode("utf-8")
    length = len(key)
    # Construct the message
    message = opcode + struct.pack("!I", length) + key
    # Schedule it for sending
    sock.send(message)

    # Wait for the server reply
    data = sock.recv(1024)
    if not data:
        print("DISCONNECTED")
    else:
        print("CONNECTED")
finally:
    srv.stop()
    sock.close()