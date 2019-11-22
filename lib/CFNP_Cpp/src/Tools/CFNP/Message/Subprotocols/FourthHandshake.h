/* FOURTH_HANDSHAKE.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  This file hosts the code that is necessary for the FourthHandshake
*    subprotocol, as specified in the Cookie Factory Network Protocol (CFNP-21).
**/

#ifndef FOURTHHANDSHAKE_H
#define FOURTHHANDSHAKE_H

#include <string>
#include "../Message.h"

namespace Msg {
    namespace FourthHandshake {
        const char subcode = 0;
        const char operators = 2;

        /* Returns the opcode from an operator in the FourthHandshake subprocol with given opcode. Returns -1 if that operator isn't found. */
        char getOperatorByName(std::string name);

        /* Returns a new instance of a desired Operator in the FourthHandshake subprotocol of the type specified by an opcode. Returns NULL if the operator isn't found. */
        Message* getOperatorObject(char subcode);
        /* Returns a new instance of a desired Operator in the FourthHandshake subprotocol of the type specified by a operator name. Returns NULL if the operator isn't found. */
        Message* getOperatorObject(std::string name);

        class ConnectionRequest: public Message {
            public:
                /* The password stored in this ConnectionRequest. */
                std::string password;

                /* The ConnectionRequest operator is used to request connection with a server by sending a password to it. (CFNP-211) */
                ConnectionRequest();
                
                /* Parses given bytes to a ConnectionRequest. The bytes are given in the pointer bytes, and bytes_size must be their length. */
                void parse(char *bytes, size_t bytes_size);
                /* Packs this ConnectionRequest to bytes. The given result pointer will be a newly allocated byte array, and result_size will be its size. */
                void pack(char **result, size_t *result_size);
        };

        class ConnectionAccept: public Message {
            public:
                /* The ConnectionAccept operator is used to accept a requested connection with a server. It doesn't send anything other than it's subcode and opcode and the like. (CFNP-212) */
                ConnectionAccept();

                /* Parses given bytes to a ConnectionAccept, but, in reality, does exactly nothing. */
                void parse(char *bytes, size_t bytes_size);
                /* Packs this ConnectionAccept to bytes. The given result pointer will be newly allocated and also completely empty. result_size will therefore be 0. */
                void pack(char **result, size_t *result_size);
        };
    }
}

#endif