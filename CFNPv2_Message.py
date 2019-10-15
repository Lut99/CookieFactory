# CFNPv2_MESSAGE.py
#   by tHE iNCREDIBLE mACHINE
#
# A script that can be imported by Interface.py to have an easy and structured
#   way to parse CFNPv2 messages

import struct
import CFNPv2_Codes as CFNP

UNIFIED_MESSAGE_STRUCTURE_FORMAT = struct.Struct("!BBIH")


# Error classes
class MessageException(Exception):
    pass
class InvalidCodeException(MessageException):
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
class ParseException(MessageException):
    pass
class PackException(MessageException):
    pass


# OpcodeMapping classes
class OpcodeField():
    """
        Allows a field to be defined for the OpcodeMap. Also parses / packs
        this field.
    """

    LENGTH_REST = -1

    # Data types
    UINT8 = "!B"
    UINT32 = "!I"
    UINT64 = "!Q"
    STR = "str"
    DATA_TYPES = [UINT8, UINT32, UINT64, STR]

    def __init__(self, field_name, length, data_type):
        # Store the values
        self.field_name = field_name
        self.length = length
        self.data_type = data_type

        # Check if length is somewhat acceptable
        if self.length < 0 and self.length != OpcodeField.LENGTH_REST:
            raise InvalidMappingException(f"Invalid length '{self.length}' (can only be >= 0 or {OpcodeHeader.LENGTH_REST})")
        # Check if the data_type is any of the data_types
        if self.data_type not in OpcodeField.DATA_TYPES:
            raise InvalidMappingException(f"Unknown data type '{self.data_type}'")

    def __str__(self):
        """ Returns the string representation of this header, aka the name """
        return self.field_name

    def parse(self, raw_chunk):
        """ Parses a single chunk (e.g., single data field) in a message """
        # Find the correct datatype
        if self.data_type == OpcodeField.STR:
            try:
                return self.field_name, raw_chunk.decode("utf-8")
            except UnicodeDecodeError as e:
                raise ParseException(f"Could not parse {raw_chunk} as string:\n{e}")
        else:
            try:
                return self.field_name, struct.unpack(self.data_type, raw_chunk)[0]
            except struct.error as e:
                raise ParseException(f"Could not parse {raw_chunk} using struct format {self.data_type}:\n{e}")

    def pack(self, value):
        """
            Tries to pack given value into binary, according to the opcode
            stored internally.
        """

        if self.data_type == OpcodeField.STR:
            try:
                return value.encode("utf-8")
            except UnicodeEncodeError as e:
                raise PackException(f"Could not pack {value} as string:\n{e}")
        else:
            try:
                return struct.pack(self.data_type, value)
            except struct.error as e:
                raise PackException(f"Could not pack {value} using struct format {self.data_type}:\n{e}")


class OpcodeMap():
    class Iterator():
        def __init__(self, raw_message, headers):
            self.raw_message = raw_message
            self.headers = headers
            self.i = 0

        def __iter__(self):
            """ Returns itself, as this iterator """
            return self

        def __next__(self):
            """ Returns the next field of the raw_message, parsed """
            # Stop if we're going too far
            if self.i >= len(self.headers):
                raise StopIteration()
            # Get the correct header
            header = self.headers[self.i]
            # Get the correct chunk of raw_message
            if header.length == OpcodeField.LENGTH_REST:
                chunk = self.raw_message
                self.raw_message = ""
            else:
                chunk = self.raw_message[:header.length]
                self.raw_message = self.raw_message[header.length:]
            # Parse it
            field_name, value = header.parse(chunk)
            # Increment self.i
            self.i += 1
            return field_name, value, len(chunk)

    def __init__(self, code, *mappings):
        if type(code) != tuple and len(code) != 2:
            raise TypeError("code must be a tuple with (subcode, opcode)")
        self.subcode = code[0]
        self.opcode = code[1]
        if self.subcode not in CFNP.TYPES:
            raise ValueError(f"subcode {self.subcode} is invalid")
        if self.opcode not in CFNP.TYPES[self.subcode].opcodes:
            raise ValueError(f"opcode {self.opcode} is invalid for subprotocol {self.subcode}")
        self.code = code
        self.headers = []
        self.fields = []
        self.length = 0
        length_rest = False
        for i, mapping in enumerate(mappings):
            # Check if the mapping is an OpcodeHeader
            if type(mapping) != OpcodeField:
                raise InvalidMappingException(f"Can only add OpcodeHeaders as map elements (header {i})")
            # Check if the mapping uses a unique field
            if mapping.field_name in self.fields:
                raise InvalidMappingException(f"Duplicate field name '{mapping.field_name}' in header {i}")
            self.fields.append(mapping.field_name)
            # Store it in the headers
            self.headers.append(mapping)
            if mapping.length == OpcodeField.LENGTH_REST:
                # Check if we're not conflicting with a previous length_rest
                if length_rest:
                    raise InvalidMappingException(f"Double length until end detected (header {i})")
                # Set the length rest
                length_rest = True
            else:
                if length_rest:
                    raise InvalidMappingException(f"Header after length until end detected (header {i})")
                # If there is a length_rest, it'll be funky
                self.length += mapping.length

    def parse(self, raw_message):
        """ Used to iteratively parse raw_message. """
        # Check if the raw_message length is enough
        if len(raw_message) < self.length:
            raise LengthException(f"Message '{raw_message}' is too short for operation {self.code}")
        return OpcodeMap.Iterator(raw_message, self.headers)

    def parse_safely(self, raw_message):
        """
            Wrapper for self.parse(). Catches errors and returns them
            rather than throwing them.
        """

        try:
            return self.parse(raw_message)
        except MessageException as e:
            return None, e

    def pack(self, values):
        """
            Tries to pack given fields according to the internal mapping.
        """

        raw_message = b""
        done = 0
        for i, value in enumerate(values):
            if i >= len(self.headers):
                raise LengthException(f"Cannot parse value {i} as the mapping has ended")
            # Parse it using the header
            header = self.headers[i]
            raw_message += header.pack(value)
            done += 1
        # Check if we still have some to go
        if done < len(self.headers) - 1:
            raise LengthException(f"Missing {len(self.headers) - 1 - i} values")
        # Done, return the packed message
        return raw_message

    def pack_safely(self, values):
        """
            Wrapper for self.pack(). Catches errors and returns them rather
            than throwing them.
        """

        try:
            return True, self.pack(values)
        except MessageException as e:
            return False, e


# The class this is all about: the Message class
class Message():
    """
        The Message class. A container for all message data, including
        several fields and the type of fields.
    """

    # Opcode mappings
    # Each opcode has it's own header structure, which is defined below
    SUBOP_MAPPING = {
        CFNP.FOURTH_HANDSHAKE.REQUEST: OpcodeMap(
            CFNP.FOURTH_HANDSHAKE.REQUEST,
            OpcodeField("password", OpcodeField.LENGTH_REST, OpcodeField.STR)
        ),
        CFNP.FOURTH_HANDSHAKE.ACCEPT: OpcodeMap(
            CFNP.FOURTH_HANDSHAKE.ACCEPT
        ),
        CFNP.TERMINAL.ANNOUNCEMENT: OpcodeMap(
            CFNP.TERMINAL.ANNOUNCEMENT,
            OpcodeField("checksum", 8, OpcodeField.UINT64)
        ),
        CFNP.TERMINAL.ANNOUNCEMENT_MESSAGE: OpcodeMap(
            CFNP.TERMINAL.ANNOUNCEMENT_MESSAGE,
            OpcodeField("error_code", 1, OpcodeField.UINT8),
            OpcodeField("real_timestamp", 8, OpcodeField.UINT64),
            OpcodeField("simu_timestamp", 8, OpcodeField.UINT64),
            OpcodeField("origin", 36, OpcodeField.STR),
            OpcodeField("message", -1, OpcodeField.STR)
        ),
        CFNP.TERMINAL.COMMAND_REQUEST: OpcodeMap(
            CFNP.TERMINAL.ANNOUNCEMENT_MESSAGE,
            OpcodeField("real_timestamp", 8, OpcodeField.UINT64),
            OpcodeField("message", -1, OpcodeField.STR)
        ),
        CFNP.TERMINAL.COMMAND_RESPONSE: OpcodeMap(
            CFNP.TERMINAL.COMMAND_RESPONSE,
            OpcodeField("error_code", 1, OpcodeField.UINT8),
            OpcodeField("real_timestamp", 8, OpcodeField.UINT64),
            OpcodeField("message", -1, OpcodeField.STR)
        ),
        CFNP.TERMINAL.SYNC_REQUEST: OpcodeMap(
            CFNP.TERMINAL.SYNC_REQUEST
        ),
        CFNP.TERMINAL.SYNC_RESPONSE: OpcodeMap(
            CFNP.TERMINAL.SYNC_RESPONSE,
            OpcodeField("checksum", 8, OpcodeField.UINT64),
            OpcodeField("real_timestamp", 8, OpcodeField.UINT64)
        )
    }

    def __init__(self, code, raw_message=None):
        if type(code) != tuple and len(code) != 2:
            raise TypeError("code must be a tuple with (subcode, opcode)")
        self.subcode = code[0]
        self.opcode = code[1]
        if self.subcode not in CFNP.TYPES:
            raise ValueError(f"subcode {self.subcode} is invalid")
        if self.opcode not in CFNP.TYPES[self.subcode].opcodes:
            raise ValueError(f"opcode {self.opcode} is invalid for subprotocol {self.subcode}")
        self.code = code
        self.parsed = False
        # Check if the opcode is valid
        if self.code not in Message.SUBOP_MAPPING:
            raise InvalidCodeException(f"Mapping not defined for subprotocol {self.subcode} with operator {self.opcode}")
        # Store the mapping
        self.mapping = Message.SUBOP_MAPPING[self.code]
        self.length = 0

        if raw_message is None:
            # We're done, no need to parse
            return

        # Parse the message
        for field_name, value, b_length in self.mapping.parse(raw_message):
            # Set our own attribute as this field (if not already set)
            if hasattr(self, field_name):
                raise ValueError(f"This message object already has a {field_name} field")
            setattr(self, field_name, value)
            # Also keep track of the length
            self.length += b_length

        # Done initializing

    def pack(self):
        """ Converts the message fields back into a bytearray again """

        # First, collect all the values
        values = []
        for field in self.mapping.fields:
            if not hasattr(self, field):
                raise MissingFieldException(f"No field '{field}' specified for message of subprotocol {self.subcode} with operation {self.opcode}")
            values.append(getattr(self, field))
        # Now parse it
        return self.mapping.pack(values)

    def pack_safely(self):
        """ Similar to pack except that it packs safely """

        values = []
        for field in self.mapping.fields:
            if not hasattr(self, field):
                return False, MissingFieldException(f"No field '{field}' specified for message of subprotocol {self.subcode} with operation {self.opcode}")
            values.append(getattr(self, field))
        # Now, try to parse
        return self.mapping.pack_safely(values)

    # Handle special functions
    def __len__(self):
        return self.length

    @staticmethod
    def create(code, raw_message):
        """
            Creates a new Message object, but then without throwing
            MessageExceptions if any.
        """

        try:
            return True, Message(code, raw_message)
        except MessageException as e:
            return False, e


if __name__ == "__main__":
    def test_messages():
        # Create a test message
        test = Message(CFNP.FOURTH_HANDSHAKE.REQUEST)
        test.password = "test"

        # Convert to bytes
        bts = test.pack()
        print(f"CONNECTION_REQUEST with password 'test': {bts}")

        # Try to convert it back into a password again
        # Don't forget to exclude the general header
        test_back = Message(CFNP.FOURTH_HANDSHAKE.REQUEST, bts)
        print(f"  > Converted back to text: {test_back.password}")

        # Okay, a more difficult example:
        test = Message(CFNP.TERMINAL.COMMAND_RESPONSE)
        test.error_code = 0
        test.real_timestamp = 255
        test.message = "Hello there!"

        # Convert to bytes
        bts = test.pack()
        print(f"TERMINAL_COMMAND_RESPONSE with timestamp {test.real_timestamp}, message '{test.message}': {bts}")

        # Try to convert it back into a password again
        test_back = Message(CFNP.TERMINAL.COMMAND_RESPONSE, bts)
        print(f"  > Converted back: {test_back.error_code}, {test_back.real_timestamp}, '{test.message}'")

        # Good! Now let's try to fuck with it
        try:
            test_back = Message(CFNP.TERMINAL.COMMAND_RESPONSE, b"\x00\xFF\x25")
        except LengthException as e:
            print(e)

    # Test the above functions
    test_messages()
