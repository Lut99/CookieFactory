# MESSAGE_C.py
#   by tHE iNCREDIBLE mACHINE
#
# Description: This file wraps Message.c so that's it available in python.

from ctypes import c_int
from ctypes import c_ubyte
from ctypes import POINTER

import resources.CFNPv2.Message_H as HMessage
from resources.CFNPv2.Message_H import CMessage


class Message():
    def __init__(self, code, raw_message=None):
        # First, convert the code to C-types
        subcode = c_ubyte(code[0])
        opcode = c_ubyte(code[1])

        # Create the message struct with the correct opcode
        self._msg = HMessage.create_message(subcode, opcode)

        # If a raw_message is given, parse it
        if raw_message is not None:
            # First off, convert raw_message to bytes if possible
            c_raw_message = POINTER(raw_message)
            # Also store the length
            c_raw_message_length = c_int(len(raw_message))
            # Now parse
            HMessage.parse_message(self._msg, c_raw_message, c_raw_message_length)
            print(self._msg.raw)

    def pack(self):
        """ Packs self into a raw byte array which is returned. """
        pass


if __name__ == "__main__":
    msg = Message((0, 0), raw_message=b'Hello there!')
