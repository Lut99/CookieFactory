/* MESSAGE.c
 *   by tHE iNCREDIBLE mACHINE
 * 
 * DECRIPTION: This file contains the Message struct and the convertion to/from
 *             binary, that can be used across platform to translate messages
 *             in a constant and uniform way.
 */

#include <stdlib.h>
#include <stdio.h>
#include <limits.h>
#include "Message.h"
#include "Encoding.h"

/* Unified Message Structure encapsulation (CFNP-201) */
void encapsulate(Header *h, unsigned char* bytes, unsigned char* result) {
    /* Encapsulates given bytes with the Unified Message Structure header. The
     * result is put into the result array, which must be at least 8 + the
     * length of bytes. */
    // First, put in the header elements
    // Subcode and opcode can be done linearly
    result[0] = h->subcode;
    result[1] = h->opcode;
    // The length can be encoded
    encode_uint32(h->length, result + 2);
    // The next_up is encoded as well
    encode_uint16(h->next_up, result + 6);
    // Finally, copy the bytes array to the new one IF they don't point to the
    //   same already
    if (result + 8 != bytes) {
        int i;
        for (i = 0; i < h->length; i++) {
            result[i + 8] = bytes[0];
        }
    }
}
void decapsulate(Header* result, unsigned char* bytes) {
    /* Parses the Unified Message Structure header. Note: since this is always
     * supposed to have a length of 8, this is assumed. */
    // We can lineairly take the first two bytes as subcode and opcode
    result->subcode = bytes[0];
    result->opcode = bytes[1];
    // Parse the other four elements as an int
    result->length = decode_uint32(bytes + 2);
    // Parse the remain two bytes as a short
    result->next_up = decode_uint16(bytes + 6);
}

/*** Subprotocol Parsing ***/
/* General Parsing / Packing Selection */
unsigned char parse_message(Message *msg, unsigned char *bytes, unsigned int bytes_length) {
    /* Chooses how to parse a message and then does it like that. If it fails,
     * it returns 0 and a 1 otherwise. */
    if (msg->subcode == FOURTH_HANDSHAKE) {
        if (msg->opcode == CONNECTION_REQUEST) {
            ConnectionRequest *c = (ConnectionRequest *) msg;
            return parse_connection_request(c, bytes, bytes_length);
        } else if (msg->opcode == CONNECTION_ACCEPT) {
            ConnectionAccept *c = (ConnectionAccept *) msg;
            return parse_connection_accept(c, bytes, bytes_length);
        }
    }
    // It's an unknown message, couldn't parse
    return 0;
}
unsigned char pack_message(Message *msg) {
    /* Chooses how to pack a message and then does it like that. If it fails,
     * it returns 0 and a 1 otherwise. */
    if (msg->subcode == FOURTH_HANDSHAKE) {
        if (msg->opcode == CONNECTION_REQUEST) {
            ConnectionRequest *c = (ConnectionRequest *) msg;
            return pack_connection_request(c);
        } else if (msg->opcode == CONNECTION_ACCEPT) {
            ConnectionAccept *c = (ConnectionAccept *) msg;
            return pack_connection_accept(c);
        }
    }
    // It's an unknown message, couldn't parse
    return 0;
}

/* Fourth Handshake (CFNP-21) / Connection Request (CFNP-211) */
ConnectionRequest *create_connection_request() {
    /* Creates a Connection Request message. Note: is allocated, needs to be
     * deallocated. */
    ConnectionRequest *msg = malloc(sizeof(ConnectionRequest));
    msg->base.subcode = FOURTH_HANDSHAKE;
    msg->base.opcode = CONNECTION_REQUEST;
    msg->base.raw = NULL;
    msg->base.raw_length = UINT_MAX;
    msg->password = NULL;
    msg->password_length = UINT_MAX;
    return msg;
}
unsigned char parse_connection_request(ConnectionRequest *msg, unsigned char *bytes, unsigned int bytes_length) {
    /* Parses given bytes as if it were the fields for a Connection Request.
     * The result is stored in the given ConnectionRequest struct. Note:
     * allocates new fields, and therefore is not referencing bytes. */
    // For connectionrequest, just re-interpret the bytes as chars and copy
    //   them
    msg->password = malloc(bytes_length * sizeof(char));
    char i;
    for (i = 0; i < bytes_length; i++) {
        msg->password[i] = bytes[i];
    }
    msg->password_length = bytes_length;
    return 1;
}
unsigned char pack_connection_request(ConnectionRequest *msg) {
    /* Creates a raw byte array that is stored in msg->base.raw. Is allocated,
     * but should be automatically deallocated upon calling
     * free_connection_request. */
    if (msg->password == NULL || msg->password_length == UINT_MAX) {
        // Nothing to be done, return as not packed
        return 0;
    }
    msg->base.raw = malloc(msg->password_length * sizeof(unsigned char));
    // Copy all the data from password
    char i;
    for (i = 0; i < msg->password_length; i++) {
        msg->base.raw[i] = msg->password[i];
    }
    msg->base.raw_length = msg->password_length;
    // Succes
    return 1;
}
void free_connection_request(ConnectionRequest *msg) {
    /* Frees the allocated Connection Request. */
    if (msg->base.raw != NULL) {
        free(msg->base.raw);
    }
    if (msg->password != NULL) {
        free(msg->password);
    }
    free(msg);
}

/* Fourth Handshake (CFNP-21) / Connection Accept (CFNP-212) */
ConnectionAccept *create_connection_accept() {
    /* Creates a Connection Accept message. Note: is allocated, needs to be
     * deallocated. */
    ConnectionAccept *msg = malloc(sizeof(ConnectionAccept));
    msg->base.subcode = FOURTH_HANDSHAKE;
    msg->base.opcode = CONNECTION_REQUEST;
    msg->base.raw = NULL;
    msg->base.raw_length = UINT_MAX;
    return msg;
}
unsigned char parse_connection_accept(ConnectionAccept *msg, unsigned char *bytes, unsigned int bytes_length) {
    /* Parses given bytes as if it were the fields for a Connection Accept.
     * The result is stored in the given ConnectionAccept struct. */
    // This is very easy for parse_connection_accept, as there is no payload
    return 1;
}
unsigned char pack_connection_accept(ConnectionAccept *msg) {
    /* Creates a raw byte array that is stored in msg->base.raw.  */
    // Very easy, as there is no payload
    msg->base.raw = NULL;
    msg->base.raw_length = 0;
    // Succes
    return 1;
}
void free_connection_accept(ConnectionAccept *msg) {
    /* Frees the allocated Connection Accept. */
    free(msg);
}