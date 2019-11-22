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
void Message::parse(char *bytes, size_t bytes_size) {
    cerr << "WARNING: Parse not implemented" << endl;
}
void Message::pack(char **result, size_t *result_size) {
    cerr << "WARNING: Pack not implemented" << endl;
}

/* ConnectionAccept logic */
