from ctypes import CDLL
from ctypes import POINTER
from ctypes import Structure
from ctypes import c_int
from ctypes import c_ubyte
from ctypes import c_char_p

# Load the library
CMessage = CDLL("Message.so")

FOURTH_HANDSHAKE = CMessage.FOURTH_HANDSHAKE
CONNECTION_REQUEST = CMessage.CONNECTION_REQUEST
CONNECTION_ACCEPT = CMessage.CONNECTION_ACCEPT


# Define relevant structs
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


def create_message(code):
    # Covert the codes to ctypes
    subcode = c_ubyte(code[0])
    opcode = c_ubyte(code[1])

    # Use the C function to create a new struct
    c_create_message = CMessage.create_message
    c_create_message 
    c_create_message.restype = Message_p

    return c_create_message(subcode, opcode)
