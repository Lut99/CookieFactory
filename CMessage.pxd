# MESSAGE.pxd
#   by tHE iNCREDIBLE mACHINE
#
# This file is the Cython header for the Message Library.

cdef extern from "Message.h":
    # Define general structs
    ctypedef struct Header:
        unsigned char subcode
        unsigned char opcode
        unsigned int length
        unsigned short next_up
    
    ctypedef struct Message:
        unsigned char subcode
        unsigned char opcode
        unsigned char *raw
        unsigned int raw_length
    
    # Define the encapsulation
    unsigned char encapsulate(Header *h, unsigned char *raw, unsigned char *result)
    void decapsulate(Header *result, unsigned char *raw)

    # Define the general parse / pack
    unsigned char parse_message(Message *msg, unsigned char *raw, unsigned int bytes_length);
    unsigned char pack_message(Message *msg);

    # Define ConnectionRequest
    ctypedef struct ConnectionRequest {
        Message base
        char *password
        unsigned int password_length
    }

    ConnectionRequest *create_connection_request()
    unsigned char parse_connection_request(ConnectionRequest *msg, unsigned char *raw, unsigned int bytes_length)
    unsigned char pack_connection_request(ConnectionRequest *msg)
    void free_connection_request(ConnectionRequest *msg)

    ctypedef struct ConnectionAccept {
        Message base;
    }

    ConnectionAccept *create_connection_accept()
    unsigned char parse_connection_accept(ConnectionAccept *msg, unsigned char *bytes, unsigned int bytes_length)
    unsigned char pack_connection_accept(ConnectionAccept *msg)
    void free_connection_accept(ConnectionAccept *msg)