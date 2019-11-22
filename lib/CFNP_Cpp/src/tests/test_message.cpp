/* test_encoding.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  DESCRIPTION: This file tests Encoding.cpp.
*
**/

#include <cstdlib>
#include <ctime>
#include <sstream>
#include <iostream>
#include "../Tools/CFNP/CFNP.h"

using namespace std;
using namespace Msg;
using namespace Msg::FourthHandshake;


string str_hex(char *bytes, int bytes_size) {
    stringstream sstr;
    sstr << "[";
    for (int i = 0; i < bytes_size; i++) {
        if (i > 0) {sstr << ",";}
        sstr << "0x" << hex << (((int) (bytes[i])) & 0xFF);
    }
    sstr << "]";
    return sstr.str();
}


bool test_connection_request(string to_check) {
    cout << "Testing ConnectionRequest..." << endl;

    // Create a ConnectionRequest object
    ConnectionRequest req = ConnectionRequest();
    // Provide it with data
    req.password = to_check;

    // Pack it to raw bytes
    char *result;
    size_t size;
    req.pack(&result, &size);

    // Parse it back and do the stuff
    ConnectionRequest req_back = ConnectionRequest();
    req_back.parse(result, size);

    delete[](result);

    // Check the strings
    if (req_back.password.compare(to_check) == 0) {
        cout << " > Succes" << endl;
        return true;
    } else {
        cout << " > Failure: expected \"" << to_check << "\", got \"" << req_back.password << "\"" << endl;
        return false;
    }
}
bool test_connection_accept() {
    cout << "Testing ConnectionAccept..." << endl;

    // Create a connectionaccept object
    ConnectionAccept acp = ConnectionAccept();
    if (acp.subcode != 0 && acp.opcode != 1) {
        cout << " > Failure: opcode and subcode are not (0, 1)" << endl;
        return false;
    } else {
        cout << " > Succes" << endl;
        return true;
    }
}


int main() {
    test_connection_request("KAHSdkajhsdkhasd");
    test_connection_accept();
}