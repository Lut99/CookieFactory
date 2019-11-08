# distutils: sources = src/C/Message.c
# distutils: include_dirs = src/C
# distutils: language=c
# cython: language_level=3

cimport CMessage

class CFNP_Errors:
    class CFNPException(Exception):
        pass
    class NotInitialised(CFNPException):
        pass
    class FieldEmptyException(CFNPException):
        pass

cdef class Message:
    cdef unsigned char subcode;
    cdef unsigned char opcode;
    cdef CMessage.Message *msg;

    def __cinit__(self):
        self.msg = NULL

    def __dealloc__(self):
        if self.msg:
            CMessage.free_message(self.msg)
    
    def _parse(self, code, raw_message):
        # First, check if we have an object
        if not self.msg:
            raise CFNP_Errors.NotInitialised()
        # Next, parse the given byte stream
        CMessage.parse_message(<CMessage.Message*> self.msg, <unsigned char*> raw_message, <unsigned int> len(raw_message))
        # Done, as the result is in self.msg

# Now follow all subclasses of Message
cdef class ConnectionRequest(Message):
    def __init__(self):
        self.subcode = CMessage.FOURTH_HANDSHAKE
        self.opcode = CMessage.CONNECTION_REQUEST

        # Also create the message object
        self.msg = <CMessage.Message*> CMessage.create_connection_request()
        if not self.msg:
            raise MemoryError()

        # Declare empty placeholder for password
        self.password = None
        self._prev_password = None
    
    def parse(self, raw_message):
        """
            Parses the raw_message and stores the result in the fields of this
            class.
        """

        self._parse((self.subcode, self.opcode), raw_message)
        # Extract the relevant fields, namely password
        self.password = (<bytes> (<CMessage.ConnectionRequest*> self.msg).password).decode("utf-8")

    def pack(self):
        """ Packs this class into a byte array """
        # First, check if password is set
        if self.password is None:
            raise CFNP_Errors.FieldEmptyException()
        # Only update self.msg.base.raw if the password has changed
        if self.password != self._prev_password:
            (<CMessage.ConnectionRequest*> self.msg).password = <char*> self.password
            # Pack it
            CMessage.pack_connection_request(<CMessage.ConnectionRequest*> self.msg)
            # Update the previous password
            self._prev_password = self.password

        # Return the raw value
        return <bytes> self.msg.raw

cdef class ConnectionAccept(Message):
    def __init__(self):
        self.subcode = CMessage.FOURTH_HANDSHAKE
        self.opcode = CMessage.CONNECTION_ACCEPT

        # Also create the message object
        self.msg = <CMessage.Message*> CMessage.create_connection_accept()
        if not self.msg:
            raise MemoryError()
        
        # Declare nothing as this is a ridiculously simple operator
    
    def parse(self, raw_message):
        """
            Parses the raw_message. But since nothing needs doing, nothing is
            done.
        """

        pass
    
    def pack(self):
        """ Packs this class into a byte array """
        
        pass