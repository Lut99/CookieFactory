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
            void pack(char **result, size_t *result_size);
    };
}

#endif