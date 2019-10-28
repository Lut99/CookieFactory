# INTERFACE.py
#   by tHE iNCREDIBLE mACHINE
#
# A script that hosts the interface functions of World.py. Works on TCP-connections,
#   and is designed to accept multiple interfaces at once.

import socket
import ssl
import os
import select
import threading
import time
import struct

import Globals
from Globals import register_uuid
from Globals import UUID_MAP
from CFNPv2_Message import Message
import CFNPv2_Codes as CFNP

BUFFER_SIZE = 1024
KEY = "9zTw%V'VLl%R0,@,4;IQ~(/@UDT*|=,3"
PENDING_TIMEOUT = 3

MAX_TERMINAL_SIZE = 1024


class TerminalData():
    """
        Stores Terminal Announcement Messages as efficiently as possible, while
        still also maintaining a checksum of all messages.
    """

    def __init__(self, max_size=MAX_TERMINAL_SIZE):
        self.max_size = max_size
        if self.max_size > 0xFFFFFFFF:
            raise ValueError(f"max_size can be at most {int(0xFFFFFFFF)}")
        self.size = 0
        self.checksum = 0
        self._raw = b""
        self._lengths = b""
        self._struct = struct.Struct("!I")

    def store(self, message):
        """
            Stores a new message in the inner __raw__ dict and updates
            self.checksum
        """

        if type(message) == Message:
            message = Message.pack()
        elif type(message) != bytes:
            raise TypeError("message can only be bytes or Message object")

        # First, check for enough space
        s_message = len(message)
        if self.size + s_message > self.max_size:
            # Remove the first one
            s = self._struct.unpack(self._lengths[:4])[0]
            self._lengths = self._lengths[4:]
            self._raw = self._raw[s:]
            self.size -= s

        # Add the message to the raw heap and it's length to the lengths heap
        self._raw += message
        self._lengths += self._struct.pack(s_message)
        self.size += s_message
        # Compute the new checksum
        self.checksum = hash(self._raw)


class Interface ():
    """ Handles communication to a single, remote interface. """

    def __init__(self, addr, port, conn):
        self.addr = addr
        self.port = port
        self.addrstr = f"{self.addr}:{self.port}"
        self.name = f"Interface_{self.addrstr}"
        self.conn = conn

        # Already init the struct for the Unified Message Header (CFNP-201)
        self.struct = struct.Struct("!BBIH")

        # Ready the message queue
        self.message_queue = []

        # Finally, store the creation time
        self.created = time.time()

        self.log("Created")

    # NETWORK
    def receive(self):
        """
            Receives messages in the Cookie Factory Network Protocol (CFNPv2).
            The receiving goes in accordance with CFNP-201
        """
        # First, receive the general header (1 + 1 + 4 + 2 bytes)
        header = self.conn.recv(8)
        if not header:
            # Other side probably closed
            return [((-1, -1), None)]
        # Parse the message
        subcode, opcode, length, next_messages = self.struct.unpack(header)
        # Receive the other length of data
        data = b""
        while len(data) < length:
            data = self.conn.recv(length - len(data))
            # Break at any time if empty, because then we disconnected
            if not data:
                return [((-1, -1), None)]
        # Covert it to a message
        succes, msg = Message.create((subcode, opcode), data)
        if not succes:
            self.log(f"Received invalid message that couldn't be parsed:\n{msg}")
            return [((-1, -1), None)]
        # Before returning, pass any other messages (if any)
        messages = [((subcode, opcode), msg)]
        if next_messages > 0:
            other_messages = self.receive()
            messages += other_messages
        # Return everything
        return messages

    def send(self, message, next_up=[]):
        """ Ready a message to be send according to the CFNPv2 """
        if type(message) != Message:
            raise TypeError("Can only send Message objects")
        # Convert it to the byte representation
        raw_data = message.pack()
        # Prepend the opcode and the length
        raw_data = self.struct.pack(message.subcode, message.opcode, len(raw_data), len(next_up)) + raw_data
        # Schedule it for sending
        self.message_queue.append(raw_data)
        if len(next_up) > 0:
            # Recursively do the rest of next_up
            self.send(next_up[0], next_up[1:])

    def flush_first(self):
        """ Gets the first message in the queue and sends it """
        if len(self.message_queue) == 0:
            # Nothing to send
            return
        msg = self.message_queue.pop(0)
        self.conn.send(msg)

    def close(self):
        """ Closes the connection """
        self.conn.close()
        self.log("Closed")

    def fileno(self):
        """ Wraps the internal conn fileno """
        return self.conn.fileno()

    # TOOLS
    def log(self, text, end="\n"):
        print(f"[{self.name}] {text}", end=end)


class ConnectionServer (threading.Thread):
    """
        Handles all incoming and outgoing communications in a Cookie Factory
        World using Interfaces.
    """

    def __init__(self, ip_address="", port=8080):
        threading.Thread.__init__(self)
        self.name = "ConnectionServer"

        # Ready the interfaces list
        self.interfaces = []
        # Ready the list that listens for new users
        self.pending = []
        # Ready the raw byte string of all messages received
        self.announcements = TerminalData()

        # Store the simulated time object
        self.time = Globals.TIME
        # Store a uuid for server messages
        self.uuid = register_uuid("World")

        # Initialise the server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip_address, port))
        self.sock.listen(5)
        log_message = f"Opened server on port {port}"
        if ip_address != "":
            log_message += f" bound to {ip_address}"
        self.log(log_message)

        self.log("Created")

    # THREAD
    def run(self):
        self.running = True
        self.log("Started")
        try:
            while self.running:
                # Get the available sockets
                read_ready, write_ready, _ = select.select([self.sock] + self.interfaces + self.pending, self.interfaces, [], 0)
                for interface in read_ready:
                    if interface == self.sock:
                        # New connection incoming: accept it
                        conn, addr = self.sock.accept()
                        self.log(f"New connection attempt from: {addr}")
                        # Warp them in an interface and store them under the
                        #   temporary connections
                        client = Interface(addr[0], addr[1], conn)
                        self.pending.append(client)
                    elif interface in self.pending:
                        # The interface has send us a message while pending
                        code, msg = interface.receive()[0]
                        # Only allow the user onward if he sends the correct password
                        if code != CFNP.FOURTH_HANDSHAKE.REQUEST or msg.password != KEY:
                            # Drop the user harder than third period french
                            interface.close()
                            self.pending.remove(interface)
                            self.log(f"Dropped user {interface.addrstr} because security check failed")
                            continue
                        # Send the user a Connection Accept
                        interface.send(Message(CFNP.FOURTH_HANDSHAKE.ACCEPT))
                        # Move from pending to interface
                        self.pending.remove(interface)
                        self.interfaces.append(interface)
                        self.log(f"User {interface.addrstr} succesfully authenticated")
                    else:
                        messages = interface.receive()
                        if messages[0][0] == (-1, -1):
                            # User closed the connection
                            self.interfaces.remove(interface)
                            self.log(f"User {interface.addrstr} closed the connection")
                            continue
                        # Otherwise, run the opcode trough the parser and let it deal with it
                        self.handle_message(interface, messages)
                for interface in write_ready:
                    # Flush the first message of the interface and send it
                    interface.flush_first()

                # Check if any of the pending connections have timed out
                for interface in self.pending.copy():
                    if time.time() - interface.created > PENDING_TIMEOUT:
                        # Drop the user harder than third period french
                        interface.close()
                        self.pending.remove(interface)
                        self.log(f"Dropped user {interface.addrstr} because security check timed out")
                        continue

        finally:
            self.log("Closing server...")
            self.sock.close()
            print("Closed server.")

    def stop(self):
        # Stop the Thread
        if not self.running:
            self.log("Already stopped")
            return
        # Set the stop flag, then wait until quitted
        self.running = False
        self.log("Stopping Connection thread...")
        while self.isAlive():
            pass
        # Stop the interfaces & pending
        for interface in self.interfaces + self.pending:
            interface.close()
        self.log("Stopped")

    # NETWORK
    def broadcast(self, message, next_up=[]):
        """ Broadcasts a message to all connected interfaces """
        if type(message) != Message:
            raise TypeError("Can only send Message objects")

        for i in self.interfaces:
            i.send(message, next_up)

    # TERMINAL RELATED
    def announce(self, message, error_code=0, origin=None):
        # Replace the origin if needed
        if origin is None:
            origin = self.uuid

        # Find the correct origin map

        # Construct a terminal message
        msg = Message(CFNP.TERMINAL.ANNOUNCEMENT_MESSAGE)
        msg.error_code = error_code
        msg.real_timestamp = int(time.time() * 1000)
        msg.simu_timestamp = self.time.epoch
        msg.origin = origin
        msg.message = message

        # Store the message in the internal terminal object and use that to
        #   create a new hash
        #self.announcements.store(msg.pack())
        #announcement = Message(CFNP.TERMINAL.ANNOUNCEMENT)
        #announcement.checksum = self.announcements.checksum

        # Send it on it's way
        #self.broadcast(announcement, next_up=[msg])

        # Also print locally for prettiness
        #print(f"[{self.now()}][{UUID_MAP[origin]}] {message}", end="")

    # TOOLS
    def log(self, text, end="\n"):
        print(f"[{self.now()}][{self.name}] {text}", end=end)

    def handle_message(self, sender, message):
        """
            Parses a message according to given opcode and then decides what to
            do with it.
            Note: even though there are more opcodes than handled here, this
            function will only handle those relevant for the server-side
        """

        # Decide on the proper action
        pass

    def now(self):
        return time.strftime("%H:%M:%S")


def test_server():
    # Run the Connection Server on a separate thread
    srv = ConnectionServer()
    srv.start()

    # Create a socket and connect to the local server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.connect(("localhost", 8080))

        # Make connection
        # Make sure the opcode is 8 bit long
        code = CFNP.FOURTH_HANDSHAKE.REQUEST
        key = (KEY).encode("utf-8")
        header = struct.pack("!BBIH", code[0], code[1], len(key), 0)
        # Construct the message
        message = header + key
        # Schedule it for sending
        sock.send(message)

        # Wait for the server reply
        data = sock.recv(1024)
        if not data:
            print("DISCONNECTED")
        else:
            subcode, opcode, length, next_up = struct.unpack("!BBIH", data[:8])
            print(subcode, opcode, length, next_up)
            print("ACCESS GRANTED")

        # We have access

    finally:
        srv.stop()
        sock.close()


if __name__ == "__main__":
    # Run tests
    test_server()
