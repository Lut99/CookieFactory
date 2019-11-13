from ctypes import CDLL
from ctypes import POINTER
from ctypes import Structure
from ctypes import c_int
from ctypes import c_ubyte
from ctypes import c_char_p

# Load the library
CMessage = CDLL("resources/CFNPv2/Message.so")

FOURTH_HANDSHAKE = CMessage.FOURTH_HANDSHAKE
CONNECTION_REQUEST = CMessage.CONNECTION_REQUEST
CONNECTION_ACCEPT = CMessage.CONNECTION_ACCEPT


""" Define relevant structs """
class Message(Structure):
    _fields_ = [("subcode", c_ubyte),
                ("opcode", c_ubyte),
                ("raw", c_char_p),
                ("raw_length", c_int)]
Message_p = POINTER(Message)


class ConnectionRequest(Structure):
    _fields_ = [("base", Message),
                ("password", c_char_p)]
ConnectionRequest_p = POINTER(ConnectionRequest)


class ConnectionAccept(Structure):
    _fields_ = [("base", Message)]
ConnectionAccept_p = POINTER(ConnectionAccept)


""" Define relevant functions """
# General message operations
create_message = CMessage.create_message
create_message.argtypes = [c_ubyte, c_ubyte]
create_message.restype = Message_p

parse_message = CMessage.parse_message
parse_message.argtypes = [Message_p, c_char_p, c_int]
parse_message.restype = None

free_message = CMessage.free_message
free_message.argtypes = [Message_p]
free_message.restype = None
