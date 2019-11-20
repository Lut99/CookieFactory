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
    };

    class ConnectionRequest: public Message {
        public:
            ConnectionRequest();
    };
}

#endif