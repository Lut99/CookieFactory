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

BUFFER_SIZE = 1024
KEY = "9zTw%V'VLl%R0,@,4;IQ~(/@UDT*|=,3"  # Must be 32 characters / 256 bits long
PENDING_TIMEOUT = 3

DEFAULT_MAILBOX_SIZE = 256
DEFAULT_MAILBOX_OVERFLOW_MODE = 0

# Define the operator codes
TIMEOUT = -1
CONNECTION_REQUEST = 0
CONNECTION_ACCEPT = 1
TERMINAL_PUBLIC_OUTPUT_SEND = 2
TERMINAL_PRIVATE_OUTPUT_SEND = 3
TERMINAL_INPUT_SEND = 4
TERMINAL_OUTPUT_SYNC_REQUEST = 5
TERMINAL_OUTPUT_SYNC_RESPONSE = 6
TERMINAL_MESSAGE = 7
OPCODE_DICT = {
    -1: "TIMEOUT",
    0: "CONNECTION_REQUEST",
    1: "CONNECTION_ACCEPT",
    2: "TERMINAL_PUBLIC_OUTPUT_SEND",
    3: "TERMINAL_PRIVATE_OUTPUT_SEND",
    4: "TERMINAL_INPUT_SEND",
    5: "TERMINAL_OUTPUT_SYNC_REQUEST",
    6: "TERMINAL_OUTPUT_SYNC_RESPONSE",
    7: "TERMINAL_MESSAGE"
}


def verify_mapping():
    """
        Verifies the mappings specified in Message.OPCODE_MAPPING. Needs to
        be run only once, at the start of the program, then never again.
    """

    # Verify the mappings internally
    for opcode in Message.OPCODE_MAPPING:
        i = 0
        for t in Message.OPCODE_MAPPING[opcode]:
            i += 1
            # Check if it's a tuple of the correct length
            if type(t) != tuple or len(t) != 3:
                raise Message.InvalidMappingException(f"Mapping {i} for opcode {opcode} does not consist of a tuple with length 3")
            # Check if the first argument is string, second is int >= -1, third is format string
            name, length, form = t
            if type(name) != str:
                raise Message.InvalidMappingException(f"Mapping {i} for opcode {opcode} has an invalid name field")
            if type(length) != int or length < -1:
                raise Message.InvalidMappingException(f"Mapping {i} for opcode {opcode} has an invalid length field")
            if type(form) != str:
                raise Message.InvalidMappingException(f"Mapping {i} for opcode {opcode} has an invalid format field")
            # Check if the length is valid, i.e. -1 only occurs at specific points in the mapping
            if length == -1 and i != len(Message.OPCODE_MAPPING[opcode]) and form[:3] != "sub":
                raise Message.InvalidMappingException(f"Mapping {i} for opcode {opcode} has an unexpected -1")
            # Check if format is in the correct recursion format
            if form == "sub" or form == "subp":
                # Check if that opcode exists
                if length not in Message.OPCODE_MAPPING:
                    raise Message.InvalidMappingException(f"Mapping {i} for opcode {opcode} has an unknown opcode {length} in '{form}'")
                # If it exists, make sure that there's a length field
                if Message.OPCODE_MAPPING[length][0][0] != "length":
                    raise Message.InvalidMappingException(f"Mapping {i} for opcode {opcode} refers to subprotocol without length field")


class Message:
    """
        The Message class. A container for all message data, including
        several fields and the type of fields.
    """

    # Opcode mappings
    # Each opcode has it's own header structure, which is defined below
    # Each element in the dict is a list of header elements, which in turn
    #   is a tuple with: header_name, length, format (the format is struct
    #   compliant). Only the first element is something special, namely the
    #   total length of the header (content excluded)
    # A length of -1 means that it has a length until the end of the message,
    #   thus the content
    # A format of "str" means that it is a string and needs to be
    #   encoded/decoded using '.decode("utf-8")'
    # A format of "sub<no>" means that the rest of the message is formatted
    #   as one of the other subprotocols. If this format string is appended
    #   with 'p', then that subprotocol is repeated any number of times for
    #   the remainder of the message. Note: If the defined subprotocol has
    #   a variable length but no way of defining how long exactly, this will
    #   raise a VagueNesting exception. Note: For single subprotocol nesting,
    #   the original field name will be dropped and replaced by the names
    #   generated from the nested subprotocol.
    OPCODE_MAPPING = {
        # CONNECTION_REQUEST
        0: [
            ("password", -1, "str")
        ],
        # CONNECTION_RESPONSE
        1: [],
        # TERMINAL_PUBLIC_OUTPUT_SEND
        2: [
            ("checksum", 8, "!Q"),
            ("message", 7, "sub")
        ],
        # TERMINAL_PRIVATE_OUTPUT_SEND
        3: [
            ("error_status", 1, "!B"),
            ("real_timestamp", 8, "!Q"),
            ("message", -1, "str")
        ],
        # TERMINAL_INPUT_SEND
        4: [
            ("real_timestamp", 8, "!Q"),
            ("message", -1, "str")
        ],
        # TERMINAL_SYNC_REQUEST
        5: [],
        # TERMINAL_SYNC_RESPONSE
        6: [
            ("checksum", 8, "!Q"),
            ("real_timestamp", 8, "!Q"),
            ("messages", 7, "subp")
        ],
        # TERMINAL_SYNC_MESSAGE
        7: [
            ("length", 8, "!Q"),
            ("error_status", 1, "!B"),
            ("real_timestamp", 8, "!Q"),
            ("simu_timestamp", 8, "!Q"),
            ("origin", 36, "str"),
            ("message", -1, "str")
        ]
    }

    # Error classes
    class MessageException(Exception):
        pass
    class InvalidOpcodeException(MessageException):
        pass
    class LengthException(MessageException):
        pass
    class InvalidFormatException(MessageException):
        pass
    class RecursionLoopException(MessageException):
        pass
    class MissingFieldException(MessageException):
        pass
    class InvalidMappingException(MessageException):
        pass

    def __init__(self, opcode, raw_message=None, __mapping__=None, __path__=[]):
        self.opcode = opcode
        # Check if the opcode is valid
        if self.opcode not in Message.OPCODE_MAPPING:
            raise Message.InvalidOpcodeException(f"Unknown opcode: {self.opcode}")
        self.mapping = Message.OPCODE_MAPPING[self.opcode]
        # Overwrite the mapping if given
        if __mapping__ is not None:
            self.mapping = __mapping__

        # If no raw_message is specified, nothing to parse
        if raw_message is None:
            return

        # Parse the raw_message using the specified mapping
        for element_name, element_length, parse_format in self.mapping:
            if element_length == -1:
                # Simply do the rest of the raw_message
                element_length = len(raw_message)

                # Get the chunk of this length
                chunk = raw_message[:element_length]
                raw_message = raw_message[element_length:]
            elif parse_format != "sub" and parse_format != "subp":
                # Check if there are enough bytes left in raw_message
                if element_length > len(raw_message):
                    raise Message.LengthException(f"Given message is too short for {OPCODE_DICT[self.opcode]} (got {len(raw_message)} bytes)")

                # Get the chunk of this length
                chunk = raw_message[:element_length]
                raw_message = raw_message[element_length:]
            
            # Parse it accordingly
            result = None
            if parse_format == "str":
                # Parse it as string
                try:
                    result = chunk.decode("utf-8")
                except UnicodeDecodeError:
                    raise Message.InvalidFormatException(f"Header element {element_name} cannot be parsed as string in message")
            elif parse_format == "sub" or parse_format == "subp":
                # Parse it as a subprotocol

                # Store the element_length for later (dictates the subprotocol code)
                subprotocol_code = element_length
                length_header = Message.OPCODE_MAPPING[subprotocol_code][0]
                # Check if it didn't occur already
                if subprotocol_code in __path__:
                    raise Message.RecursionLoopException(f"Subprotocol {subprotocol_code} has already occured in this recursion session; detected loop")

                # Do this while there is data
                result = []
                while len(raw_message) > 0:
                    # Read the length of the next message
                    if len(raw_message) < length_header[1]:
                        raise Message.LengthException(f"Given message is too short for {OPCODE_DICT[self.opcode]} (got {len(raw_message)} bytes)")
                    # Read the element_length from the raw_message (length field)
                    element_length = struct.unpack(length_header[2], raw_message[:length_header[1]])[0]

                    # Grab a chunk
                    chunk = raw_message[:element_length]
                    raw_message = raw_message[element_length:]

                    # Parse this subcode
                    result.append(Message(subprotocol_code, chunk, __path__=__path__ + [self.opcode]))

                    if parse_format == "sub":
                        result = result[0]
                        break
            else:
                # Parse it using struct and the given format
                try:
                    result = struct.unpack(parse_format, chunk)[0]
                except struct.error:
                    raise Message.InvalidFormatException(f"Header element {element_name} cannot be parsed as {parse_format} in message")
            # Store this field
            setattr(self, element_name, result)

        # Done initializing

    def pack(self):
        """ Converts the message fields back into a bytearray again """

        raw_data = b""
        fields = [mapping for mapping in self.mapping]
        for mapping in fields:
            if not hasattr(self, mapping[0]):
                raise Message.MissingFieldException(f"No field '{mapping[0]}' specified for message with opcode {self.opcode}")
            value = getattr(self, mapping[0])
            if mapping[2] == "subp":
                if type(value) != list:
                    raise Message.InvalidFormatException(f"Field '{mapping[0]}' requires a list of Messages")
                for elem in value:
                    if type(elem) != Message:
                        raise Message.InvalidFormatException(f"Field '{mapping[0]}' does not only exist out of Messages")
                    raw_data += elem.pack()
            elif mapping[2] == "sub":
                if type(value) != Message:
                    raise Message.InvalidFormatException(f"Field '{mapping[0]}' is not a Message")
                raw_data += value.pack()
            elif mapping[2] == "str":
                if type(value) != str:
                    # Convert it as such
                    value = str(value)
                raw_data += value.encode("utf-8")
            else:
                # Find the correct format string
                raw_data += struct.pack(mapping[2], value)
        # Add an opcode and length field for the total data
        return raw_data

    def pack_safely(self):
        """ Wrapper for pack, but then catches errors """

        try:
            return True, self.pack()
        except Message.InvalidFormatException as e:
            return False, e

    # Handle special functions
    def __len__(self):
        return len(self.pack())

    @staticmethod
    def create(opcode, raw_message=b""):
        """
            Creates a new Message object, but then without throwing
            MessageExceptions if any
        """

        try:
            return True, Message(opcode, raw_message=raw_message)
        except Message.MessageException as e:
            return False, e


class MailBox():
    """
        The MailBox class. Allows other parts of the factory to setup a mailbox,
        and check for incoming messages that only apply to them using filters.
    """
    OVERFLOWMODE_DROP_OLD = 0
    OVERFLOWMODE_DROP_NEW = 1

    def DEFAULT_FILTER(self, _):
        """
            The most basic filter that can be aqcuired. Simply acknowledges all
            incoming messages.
        """

        return True

    def __init__(self, message_filter=None, max_size=DEFAULT_MAILBOX_SIZE, overflow_mode=DEFAULT_MAILBOX_OVERFLOW_MODE):
        self.filter = MailBox.DEFAULT_FILTER
        if message_filter is not None:
            self.filter = message_filter
        self.max_size = max_size
        self.overflow_mode = overflow_mode

        self.__queue__ = []

    def push(self, message, use_filter=True):
        """ Pushes new messages onto the mailbox """
        if type(message) != Message:
            raise TypeError("Can only push Message to the mailbox queue")

        # Check if the message is valid, stop if not
        if not use_filter or not self.filter(message):
            return False 

        # Check if there is available space
        if len(self.__queue__) == self.max_size:
            if self.overflow_mode == MailBox.OVERFLOWMODE_DROP_OLD:
                self.__queue__ = self.__queue__[1:]
            elif self.overflow_mode == MailBox.OVERFLOWMODE_DROP_NEW:
                return False

        # Push to the queue
        self.__queue__.append(message)
        return True

    def has_mail(self):
        """ Checks if there are new messages in the mailbox """
        return len(self.__queue__) > 0

    def pop(self):
        """ Returns the oldest message received """
        if not self.has_mail():
            return None
        return self.__queue__.pop(0)

    def flush(self):
        """ Returns all new messages at once """
        return self.__queue__.copy()


class Interface ():
    def __init__(self, addr, port, conn):
        self.addr = addr
        self.port = port
        self.addrstr = f"{self.addr}:{self.port}"
        self.name = f"Interface_{self.addrstr}"
        self.conn = conn

        # Ready the message queue
        self.message_queue = []

        # Finally, store the creation time
        self.created = time.time()

        self.log("Created")

    # NETWORK
    def receive(self):
        """ Receives messages in the CookieFactoryProtocol (CFNP) """
        # First, receive the general header (1 + 4 bytes)
        header = self.conn.recv(5)
        if not header:
            # Other side probably closed: return None
            return -1, header
        # Split into operator code and length
        opcode = struct.unpack("!B", header[0:1])[0]
        length = struct.unpack("!I", header[1:])[0]
        # Receive the other length of data
        data = b""
        while len(data) < length:
            data = self.conn.recv(length - len(data))
        # Covert it to a message
        succes, msg = Message.create(opcode, data)
        if not succes:
            self.log("Received invalid message that couldn't be parsed: " + msg.name)
            return -1, msg.name
        # Return everything
        return opcode, msg

    def send(self, message):
        """ Ready a message to be send according to the CFNP """
        if type(message) != Message:
            raise TypeError("Can only send Message objects")
        # Convert it to the byte representation
        succes, raw_data = message.pack_safely()
        if not succes:
            raise raw_data
        # Prepend the opcode and the length
        raw_data = struct.pack("!B", message.opcode) + struct.pack("!Q", len(raw_data)) + raw_data
        # Schedule it for sending
        self.message_queue.append(raw_data)

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
    def __init__(self, ip_address="", port=8080):
        threading.Thread.__init__(self)
        self.name = "ConnectionServer"

        # Ready the interfaces list
        self.interfaces = []
        # Ready the list that listens for new users
        self.pending = []
        # Ready the mailbox list that allows others to check for messages periodically
        self.mailboxes = []

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
                read_ready, write_ready, _ = select.select(
                    [self.sock] + self.interfaces + self.pending,
                    self.interfaces, [], 0)
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
                        opcode, msg = interface.receive()
                        # Only allow the user onward if he sends the correct password
                        if opcode != CONNECTION_REQUEST or msg.password != KEY:
                            # Drop the user harder than third period french
                            interface.close()
                            self.pending.remove(interface)
                            self.log(f"Dropped user {interface.addrstr} because security check failed")
                            continue
                        # Send the user a Connection Accept
                        interface.send(Message(CONNECTION_ACCEPT))
                        # Move from pending to interface
                        self.pending.remove(interface)
                        self.interfaces.append(interface)
                    else:
                        opcode, message = interface.receive()
                        if opcode == -1:
                            # User closed the connection
                            self.interfaces.remove(interface)
                            self.log(f"User {interface.addstr} closed the connection")
                            continue
                        # Otherwise, run the opcode trough the parser and let it deal with it
                        self.handle_message(message)
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
            self.log("Closing server...", end="")
            self.sock.close()
            print(" Done")

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
    def broadcast(self, message):
        """ Broadcasts a message to all connected interfaces """
        if type(message) != Message:
            raise TypeError("Can only send Message objects")

        for i in self.interfaces:
            i.send(message)

    # MAILBOXES
    def rent_mailbox(self, mailbox):
        """ Adds a mailbox to receive messages on to the server """
        if type(mailbox) != MailBox:
            raise TypeError("Can only register MailBox objects")

        # Check if it is already registered
        if mailbox in self.mailboxes:
            return

        # Register it
        self.mailboxes.append(mailbox)

    def stop_mailbox(self, mailbox):
        """ Removes a mailbox from listening """
        if mailbox not in self.mailboxes:
            return

        # Remove it
        self.mailboxes.remove(mailbox)

    # TOOLS
    def log(self, text, end="\n"):
        print(f"[{self.name}] {text}", end=end)

    def handle_message(self, message):
        """
            Parses a message according to given opcode and then decides what to
            do with it.
            Note: even though there are more opcodes than handled here, this
            function will only handle those relevant for the server-side
        """

        # Check if it's supposed to go into a mailbox
        for m in self.mailboxes:
            m.push(message)


def test_messages():
    # Run the verifier
    verify_mapping()

    # Create a test message
    test = Message(CONNECTION_REQUEST)
    test.password = "test"

    # Convert to bytes
    bts = test.pack()
    print(f"CONNECTION_REQUEST with password 'test': {bts}")

    # Try to convert it back into a password again
    # Don't forget to exclude the general header
    test_back = Message(CONNECTION_REQUEST, bts)
    print(f"  > Converted back to text: {test_back.password}")

    # Okay, a more difficult example:
    test = Message(TERMINAL_INPUT_SEND)
    test.real_timestamp = 255
    test.message = "Hello there!"

    # Convert to bytes
    bts = test.pack()
    print(f"TERMINAL_INPUT_SEND with timestamp {test.real_timestamp}, message '{test.message}': {bts}")

    # Try to convert it back into a password again
    test_back = Message(TERMINAL_INPUT_SEND, bts)
    print(f"  > Converted back: {test_back.real_timestamp}, '{test.message}'")

    # Good! Now let's try to fuck with it
    try:
        test_back = Message(TERMINAL_INPUT_SEND, b"\x00\xFF\x25")
    except Message.LengthException as e:
        print(e)
    print(f"  > Converted back: {test_back.real_timestamp}, '{test.message}'")

    # Hardest yet: single recursion (TERMINAL_PUBLIC_OUTPUT_SEND)
    msg = Message(TERMINAL_MESSAGE)
    smsg = "Well well, what a surprise"
    msg.length = 8 + 1 + 8 + 8 + 36 + len(smsg)
    msg.error_status = 0
    msg.real_timestamp = 32323232
    msg.simu_timestamp = 13123123
    msg.origin = "x" * 36
    msg.message = smsg

    test = Message(TERMINAL_PUBLIC_OUTPUT_SEND)
    test.checksum = 5
    test.message = msg

    # Convert to bytes
    bts = test.pack()
    print(f"TERMINAL_INPUT_SEND with data:")
    print(f"  > checksum:       {test.checksum}")
    print("  > message:")
    print(f"    > length:         {msg.length}")
    print(f"    > error_status:   {msg.error_status}")
    print(f"    > real_timestamp: {msg.real_timestamp}")
    print(f"    > simu_timestamp: {msg.simu_timestamp}")
    print(f"    > origin:         \"{msg.origin}\"")
    print(f"    > message:        {msg.message}")
    print(f": {bts}")

    # Try to convert it back into a password again
    test_back = Message(TERMINAL_PUBLIC_OUTPUT_SEND, bts)
    msg_back = test_back.message
    print(f"Converted back:")
    print(f"  > checksum:       {test_back.checksum}")
    print(f"  > length:         {msg_back.length}")
    print(f"  > error_status:   {msg_back.error_status}")
    print(f"  > real_timestamp: {msg_back.real_timestamp}")
    print(f"  > simu_timestamp: {msg_back.simu_timestamp}")
    print(f"  > origin:         {msg_back.origin}")
    print(f"  > message:        {msg_back.message}")

    # Now for the hardest-ever test: repeated recursion
    msg2 = Message(TERMINAL_MESSAGE)
    smsg2 = "Oh my! A challenger approaches!"
    msg2.length = 8 + 1 + 8 + 8 + 36 + len(smsg2)
    msg2.error_status = 1
    msg2.real_timestamp = 12121212
    msg2.simu_timestamp = 99999999
    msg2.origin = "y" * 36
    msg2.message = smsg2

    test = Message(TERMINAL_OUTPUT_SYNC_RESPONSE)
    test.checksum = 10
    test.real_timestamp = 55
    test.messages = [msg, msg2]

    # Convert to bytes
    bts = test.pack()
    print(f"TERMINAL_INPUT_SEND with data:")
    print(f"  > checksum:       {test.checksum}")
    print(f"  > real_timestamp: {test.real_timestamp}")
    print("  > messages:")
    i = 0
    for m in test.messages:
        i += 1
        print(f"    {i})")
        print(f"      > length:         {m.length}")
        print(f"      > error_status:   {m.error_status}")
        print(f"      > real_timestamp: {m.real_timestamp}")
        print(f"      > simu_timestamp: {m.simu_timestamp}")
        print(f"      > origin:         {m.origin}")
        print(f"      > message:        {m.message}")
    print(f": {bts}")

    # Try to convert it back into a password again
    test_back = Message(TERMINAL_OUTPUT_SYNC_RESPONSE, bts)
    print(f"Converted back:")
    print(f"  > checksum:       {test_back.checksum}")
    print(f"  > real_timestamp: {test_back.real_timestamp}")
    i = 0
    for mback in test_back.messages:
        i += 1
        print(f"    {i})")
        print(f"      > length:         {mback.length}")
        print(f"      > error_status:   {mback.error_status}")
        print(f"      > real_timestamp: {mback.real_timestamp}")
        print(f"      > simu_timestamp: {mback.simu_timestamp}")
        print(f"      > origin:         {mback.origin}")
        print(f"      > message:        {mback.message}")


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
        opcode = struct.pack("!B", CONNECTION_REQUEST)
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
        
        # We have access

    finally:
        srv.stop()
        sock.close()


if __name__ == "__main__":
    # Run tests
    #test_messages()
    test_server()
