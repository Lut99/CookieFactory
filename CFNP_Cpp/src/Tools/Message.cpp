/* MESSAGE.cpp
*    by tHE iNCREDIBLE mACHINE
* 
*  DECRIPTION: This file contains the Message class that can be used to send
*              CFNPv2 messages over the network. It makes use of Encoding.cpp.
**/

#include <iostream>
#include "Message.h"

using namespace std;
using namespace Msg;

/* Message logic */
Message::Message(char subcode, char opcode) {
    this->subcode = subcode;
    this->opcode = opcode;
}

/* ConnectionRequest logic */
ConnectionRequest::ConnectionRequest()
    : Message(0, 0) {
    cout << "Klaar denk?" << endl;
}


/* Test */
int main() {
    Message msg = Message(5, 4);
    cout << (int) msg.subcode << "," << (int) msg.opcode << "\n";

    ConnectionRequest req = ConnectionRequest();
    cout << (int) req.subcode << "," << (int) req.opcode << "\n";
}