"""
    TERMINAL.py
        by tHE iNCREDIBLE mACHINE

    This script is the interactive terminal that is used in the Cookie Factory.
    Aside from storing messages and additional meta information about them, the
    Terminal also maintains a checksum and easy message-to-string formatters
    so that it can be easily synced with remote terminals according to the
    Cookie Factory Network Protocol (CFNP).
"""

import struct
import time
import uuid

import Interface

MAX_MESSAGES_SIZE = 10000

# Error status constants
INFORMATION = 0
WARNING = 1
FATAL_ERROR = 2
COMMAND_INFORMATION = 3
COMMAND_PARSE_ERROR = 4
COMMAND_RUN_ERROR = 5


# Basic server object for default public sending
class SERVER():
    name = "SERVER"
    uuid = str(uuid.uuid1())


class Terminal():
    def __init__(self, connection_server, time):
        self.messages_raw = b''
        self.messages_len = []
        self.connection_server = connection_server
        self.time = time

        self.checksum = 0

    def write_private(self, target, message, error_status=COMMAND_INFORMATION):
        """
            Sends a Terminal Private Output Send over the internal connection
            server
        """

        # Create the message
        msg = Interface.Message(Interface.TERMINAL_PRIVATE_OUTPUT_SEND)
        msg.error_status = error_status
        msg.real_timestamp = int(time.time())
        msg.message = message

        # Send this message to the target
        self.connection_server.send(target, msg)

    def print_private(self, target, message, error_status=COMMAND_INFORMATION, end="\n"):
        """
            Wraps self.write_private, but then with a customizable line ending
        """

        return self.write_private(target, message + end,
                                  error_status=error_status)

    def write(self, message, sender=SERVER, error_status=INFORMATION):
        """
            Sends a Terminal Public Output Send over the internal connection
            server
        """

        # First, store the message in our internal message list
        message_raw = message.encode("utf-8")
        self.messages_raw += message_raw
        self.messages_len.append(len(message_raw))
        # Make sure to discard too many old messages
        while len(self.messages_raw) > MAX_MESSAGES_SIZE:
            to_discard = self.messages_len.pop(0)
            self.messages_raw = self.messages_raw[to_discard:]

        # Update the checksum
        self.checksum = hash(self.messages_raw)

        # Create the message object
        msg = Interface.Message(Interface.TERMINAL_PUBLIC_OUTPUT_SEND)
        msg.checksum = self.checksum
        msg.message = Interface.Message(Interface.TERMINAL_MESSAGE)
        msg.message.length = len(message_raw)
        msg.message.error_status = error_status
        msg.message.real_timestamp = int(time.time())
        msg.message.simu_timestamp = self.time.epoch
        msg.message.origin = sender.uuid
        msg.message.message = message

        # Send this message to all interfaces
        self.connection_server.broadcast(msg)

        # Also print locally
        print(f"[{self.time}, {sender.name}] {message}", end="")

    def print(self, message, sender=SERVER, error_status=INFORMATION, end="\n"):
        """ Wraps self.write, but then with a default ending character """
        self.write(message + end, sender=sender, error_status=error_status)
