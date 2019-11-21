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
void ConnectionRequest::pack(char **result, size_t *result_size) {
    // Allocate a new byte array with the required size
    int size = this->password.length();
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