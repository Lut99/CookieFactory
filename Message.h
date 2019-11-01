/* MESSAGE.h
 *   by tHE iNCREDIBLE mACHINE
 * 
 * DECRIPTION: Header file for Message.c. Also contains the code mappings for
 *             subprotocols, operators and other constants.
 */

 /* Makes sure the header is only run once */
#ifndef MESSAGE_H_
#define MESSAGE_H_

typedef struct {
    /* Struct that carries information about the Unified Message Structure
     * header (CFNP-201) */
    unsigned char subcode;
    unsigned char opcode;
    unsigned int length;
    unsigned short next_up;
} Header;

typedef struct {
    /* Base struct for all Messages. Carries information about the message
     * type, as well as fields to store the raw byte data in. */
    unsigned char subcode;
    unsigned char opcode;
    unsigned char *raw;
    unsigned int raw_length;
} Message;

/* Encapsulates a byte array with 8 more bytes, which carry information needed
 * for the Unified Message Structure (CFNP-201) */
void ums_encapsulate(Header *h, unsigned char *bytes, unsigned char *result);
/* Parses the encapsulation of a byte array that is carrying header information
 * according to the Unified Message Structure (CFNP-201) */
void ums_decapsulate(Header *result, unsigned char *bytes);

/*** Subprotocol Parsing ***/

/* General Parsing / Packing Selection */

/* Takes a message object (or children thereof) and parses those according to
 * given subcode and opcode. Calls the message-specific parse function. */
unsigned char parse_message(Message *msg, unsigned char *bytes, unsigned int bytes_length);
/* Takes a message object (or children thereof) and packs those according to
 * given subcode and opcode. Calls the message-specific pack function. */
unsigned char pack_message(Message *msg);

/* Fourth Handshake (CFNP-21) */
#define FOURTH_HANDSHAKE 0
#define CONNECTION_REQUEST 0
#define CONNECTION_ACCEPT 1

typedef struct {
    /* Struct that carries information about the Connection Request (CFNP-211) */
    Message base;
    char *password;
    unsigned int password_length;
} ConnectionRequest;
/* Creates a new Connection Request. */
ConnectionRequest *create_connection_request();
/* Parses a given raw byte array, and parses that according to a Connection
 * Request. The result is stored into msg. */
unsigned char parse_connection_request(ConnectionRequest *msg, unsigned char *bytes, unsigned int bytes_length);
/* Packs a given Connection Request to a raw byte array. The result is stored
 * in msg->base.raw, and the length of this array in msg->base.raw_length. */
unsigned char pack_connection_request(ConnectionRequest *msg);
/* Cleans up a Connection Request and possible allocs within. */
void free_connection_request(ConnectionRequest *msg);

typedef struct {
    /* Struct that carries information about the Connection Accept (CFNP-212) */
    Message base;
} ConnectionAccept;
/* Creates a new Connection Accept. */
ConnectionAccept *create_connection_accept();
/* Parses a given raw byte array, and parses that according to a Connection
 * Accept. The result is stored into msg. */
unsigned char parse_connection_accept(ConnectionAccept *msg, unsigned char *bytes, unsigned int bytes_length);
/* Packs a given Connection Accept to a raw byte array. The result is stored
 * in msg->base.raw, and the length of this array in msg->base.raw_length. */
unsigned char pack_connection_accept(ConnectionAccept *msg);
/* Cleans up a Connection Accept. */
void free_connection_accept(ConnectionAccept *msg);

#endif