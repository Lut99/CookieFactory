/* MESSAGE.cpp
*    by tHE iNCREDIBLE mACHINE
* 
*  This file hosts the code that is necessary for the FourthHandshake
*    subprotocol, as specified in the Cookie Factory Network Protocol (CFNP-21).
**/

#include <sstream>
#include "FourthHandshake.h"

using namespace std;
using namespace Msg;
using namespace FourthHandshake;

/* Operator logic */
char FourthHandshake::getOperatorByName(string name) {
    if (name.compare("ConnectionRequest") == 0) {
        return 0;
    } else if (name.compare("ConnectionAccept") == 0) {
        return 1;
    }
    return -1;
}
Message* FourthHandshake::getOperatorObject(char opcode) {
    // Find the correct object
    if (opcode == 0) {
        return new ConnectionRequest();
    } else if (opcode == 1) {
        // Init and return
        return new ConnectionAccept();
    }
    // Not found, return NULL
    return NULL;
}
Message* FourthHandshake::getOperatorObject(string name) {
    // First, resolve the name
    char opcode = FourthHandshake::getOperatorByName(name);
    if (opcode < 0) {
        return NULL;
    }
    // Now, return the object
    return FourthHandshake::getOperatorObject(opcode);
}

/* ConnectionRequest logic */
ConnectionRequest::ConnectionRequest()
    : Message(0, 0) {
    // Nothing to be done since Message() handles this
}
void ConnectionRequest::parse(char *bytes, size_t bytes_size) {
    stringstream sstr;
    // Add the bytes, but -1 to account for zero terminator
    for (int i = 0; i < bytes_size - 1; i++) {
        sstr << bytes[i];
    }
    this->password = sstr.str();
}
void ConnectionRequest::pack(char **result, size_t *result_size) {
    // Allocate a new byte array with the required size
    int size = this->password.length() + 1;
    char *res = new char[size];
    // Copy the string contents
    const char *str = this->password.c_str();
    for (int i = 0; i < size; i++) {
        res[i] = str[i];
    }
    // Make sure to return everything
    (*result) = res;
    (*result_size) = size;
}

/* ConnectionAccept logic */
ConnectionAccept::ConnectionAccept()
    : Message(0, 1) {
        // Nothing to be done since everything is handled abovely
}

void ConnectionAccept::parse(char *bytes, size_t bytes_size) {
    // Does nothing as there is no payload
}
void ConnectionAccept::pack(char **result, size_t *result_size) {
    // Declare empty memory (0 bytes) and return the size
    (*result) = new char[0];
    (*result_size) = 0;
}
