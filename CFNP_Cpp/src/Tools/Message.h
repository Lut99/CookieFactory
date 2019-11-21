/* MESSAGE.h
*    by tHE iNCREDIBLE mACHINE
*  
*  DECRIPTION: Header file for Message.cpp.
**/

#ifndef MESSAGE_H
#define MESSAGE_H

namespace Msg {
    class Message {
        public:
            char subcode;
            char opcode;

            /* Initializes the Message object. The subcode and opcode are used
             *   to identify any subprotocols and operators. */
            Message(char subcode, char opcode);

            /* Abstract for parse. The given array should contain the byte
             *   representation of the current operator. */
            void parse(char *bytes, size_t bytes_size);
            /* Abstract for pack. The given array will contain a new char array
             *   containing the byte representation of this message. */
            void pack(char *result, size_t *result_size);
    };

    class ConnectionRequest: public Message {
        public:
            /* The password stored in this ConnectionRequest. */
            string password;
            /* The size of the password. NOTE: Doesn't include '\0' */
            int password_length;

            ConnectionRequest();
            
            /* Parses given bytes to a ConnectionRequest. The bytes are given in the pointer bytes, and bytes_size must be their length. */
            void parse(char *bytes, size_t bytes_size);
            /* Packs this ConnectionRequest to bytes. The given result pointer will be a newly allocated byte array, and result_size will be its size. */
            void pack(char *result, size_t *result_size);
    };
}

#endif