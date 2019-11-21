/* MESSAGE.cpp
*    by tHE iNCREDIBLE mACHINE
* 
*  DECRIPTION: This file contains the Message class that can be used to send
*              CFNPv2 messages over the network. It makes use of Encoding.cpp.
**/

#include <iostream>
#include <sstream>
#include "Message.h"

using namespace std;
using namespace Msg;

/* Message logic */
Message::Message(char subcode, char opcode) {
    this->subcode = subcode;
    this->opcode = opcode;
}
void Message::parse(char *bytes) {
    cerr << "WARNING: Parse not implemented" << endl;
}
void Message::pack(char *result) {
    cerr << "WARNING: Pack not implemented" << endl;
}

/* ConnectionRequest logic */
ConnectionRequest::ConnectionRequest()
    : Message(0, 0) {
    // Nothing to be done since Message() handles this
}
void ConnectionRequest::parse(char *bytes, size_t bytes_size) {
    stringstream sstr;
    for (int i = 0; i < bytes_size; i++) {
        sstr << bytes[i];
    }
    this->password = sstr.str();
}
void ConnectionRequest::pack(char *result, size_t *result_size) {
    // Allocate a new byte array with the required size
    (*result_size) = this->password.length();
    result = (char*) malloc((*result_size) * sizeof(char));
    // Copy the string contents
    for (int i = 0; i < (*result_size); i++) {

    }
}


/* Test */
int main() {
    Message msg = Message(5, 4);
    cout << (int) msg.subcode << "," << (int) msg.opcode << "\n";
    msg.pack(NULL);

    ConnectionRequest req = ConnectionRequest();
    cout << (int) req.subcode << "," << (int) req.opcode << "\n";
    req.pack(NULL);

    Message req_msg = (Message) req;
    req.pack(NULL);
}