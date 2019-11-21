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
    class ConnectionRequest: public Message {
        public:
            /* The password stored in this ConnectionRequest. */
            std::string password;

            ConnectionRequest();
            
            /* Parses given bytes to a ConnectionRequest. The bytes are given in the pointer bytes, and bytes_size must be their length. */
            void parse(char *bytes, size_t bytes_size);
            /* Packs this ConnectionRequest to bytes. The given result pointer will be a newly allocated byte array, and result_size will be its size. */
            void pack(char **result, size_t *result_size);
    };
}

#endif