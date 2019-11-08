from ctypes import CDLL
from ctypes import Structure

# Load the library
CMessage = CDLL("Message.so")

# Define relevant structs
class Message(Structure):
    _fields_ = [(),
                ()]