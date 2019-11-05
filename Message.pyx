cimport CMessage
from libc.stdlib cimport malloc, free

cdef class Message:
    cdef unsigned char subcode;
    cdef unsigned char opcode;
    cdef CMessage.Message *msg;

    def __cinit__(self):
        self.msg = NULL

    def __dealloc__(self):
        if self.msg != NULL:
            CMessage.free_message(self.msg)

# Now follow all subclasses of Message
cdef class ConnectionRequest(Message):
    def __init__(self):
        self.subcode = CMessage.FOURTH_HANDSHAKE
        self.opcode = CMessage.CONNECTION_REQUEST

        # Also create the message object
        self.msg = <Message*> CMessage.create_connection_request()

        # Declare empty placeholder for password
        self.password = None
        self._prev_password = None
    
    def pack(self):
        # First, check if password is set
        if self.password == None:
            return None
        # If the passwords are the same, return the value of self.msg.base.raw
        if self.password == self._prev_password:
            return self.msg.base.raw
        
        # Next, update the inner struct
        self.msg.password = self.password
        # Pack it
        CMessage.pack_connection_request(self.msg)
