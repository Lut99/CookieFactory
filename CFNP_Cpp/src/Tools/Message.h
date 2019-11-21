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

            Message(char subcode, char opcode);

            void parse(char *bytes);
            void pack(char *result);
    };

    class ConnectionRequest: public Message {
        public:
            char *password;

            ConnectionRequest();

            void parse(char *bytes);
            void pack(char *result);
    };
}

#endif