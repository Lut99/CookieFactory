# MESSAGE_C.py
#   by tHE iNCREDIBLE mACHINE
#
# Description: This file wraps Message.c so that's it available in python.

import resources.CFNPv2.Message_H as HMessage
from resources.CFNPv2.Message_H import CMessage

# Define the structs

class Message():
    def __init__(self, code, raw_message=None):
        