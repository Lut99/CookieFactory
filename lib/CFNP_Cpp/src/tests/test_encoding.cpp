/* test_encoding.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  DESCRIPTION: This file tests Encoding.cpp.
*
**/

#include <cstdlib>
#include <ctime>
#include <iostream>
#include <sstream>
#include "../Tools/Encoding.h"

using namespace std;
using namespace Enc;

string str_hex(char *bytes, int size) {
    stringstream strm;
    strm << "(";
    for (int i = 0; i < size; i++) {
        if (i > 0) {
            strm << ",";
        }
        strm << "0x" << hex << ((int) bytes[i]);
    }
    strm << ")";
    return strm.str();
}

int main() {
    srand((unsigned)time(0)); 
    /* Test encoding on each datatype specified there */
    char t0 = rand();
    unsigned char t1 = rand();
    short t2 = rand();
    unsigned short t3 = rand();
    int t4 = rand() * -1;
    unsigned int t5 = rand() * -1;
    long t6 = ((((long) rand()) << 32) | rand()) * -1;
    unsigned long t7 = ((((long) rand()) << 32) | rand()) * -1;

    cout << "Test variables:" << endl;
    cout << "    (char) t0 = " << (int) t0 << endl;
    cout << "   (uchar) t1 = " << (int) t1 << endl;
    cout << "   (short) t2 = " << (int) t2 << endl;
    cout << "  (ushort) t3 = " << (int) t3 << endl;
    cout << "     (int) t4 = " << t4 << endl;
    cout << "    (uint) t5 = " << t5 << endl;
    cout << "    (long) t6 = " << t6 << endl;
    cout << "   (ulong) t7 = " << t7 << endl;

    char *result = (char*) malloc(8 * sizeof(char));

    cout << endl << "Results:" << endl;
    encode(result, t0);
    cout << "  t0 = " << (int) t0 << " = " << str_hex(result, 1) << " = " << (int) decode_char(result) << endl;
    encode(result, t1);
    cout << "  t1 = " << (int) t1 << " = " << str_hex(result, 1) << " = " << (int) decode_uchar(result) << endl;
    encode(result, t2);
    cout << "  t2 = " << (int) t2 << " = " << str_hex(result, 2) << " = " << (int) decode_short(result) << endl;
    encode(result, t3);
    cout << "  t3 = " << (int) t3 << " = " << str_hex(result, 2) << " = " << (int) decode_ushort(result) << endl;
    encode(result, t4);
    cout << "  t4 = " << t4 << " = " << str_hex(result, 4) << " = " << decode_int(result) << endl;
    encode(result, t5);
    cout << "  t5 = " << t5 << " = " << str_hex(result, 4) << " = " << decode_uint(result) << endl;
    encode(result, t6);
    cout << "  t6 = " << t6 << " = " << str_hex(result, 8) << " = " << decode_long(result) << endl;
    encode(result, t7);
    cout << "  t7 = " << t7 << " = " << str_hex(result, 8) << " = " << decode_ulong(result) << endl;

    free(result);

    return 0;
}