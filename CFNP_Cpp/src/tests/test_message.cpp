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
    cout << "Testing ConnectionRequests..." << endl;

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
    } else {
        cout << " > Failure: expected \"" << to_check << "\", got \"" << req_back.password << "\"" << endl;
    }
}


int main() {
    test_connection_request("KAHSdkajhsdkhasd");
}