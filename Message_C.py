# MESSAGE_C.py
#   by tHE iNCREDIBLE mACHINE
#
# Description: This file wraps Message.c so that's it available in python.

from ctypes import CDLL
from ctypes import c_void_p;

# Import the library
CMessage = CDLL("resources/CFNPv2/Message.so")

# Define the structs

class Message():
    def __init__(self, code, raw_message=None):
        