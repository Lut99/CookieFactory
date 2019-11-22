/* ENCODING.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  DECRIPTION: This file contains all sorts of functions to parse multiple
*              bytes as other formats and back.
**/

#include <iostream>
#include "Encoding.h"

/* 8-bit */
void Enc::encode(char *result, char number) {
    // Simply set the first result to number
    unsigned char *uresult = (unsigned char*) result;
    uresult[0] = (unsigned char) number;
}
void Enc::encode(char *result, unsigned char number) {
    // Simply set the first result to number
    unsigned char *uresult = (unsigned char*) result;
    uresult[0] = number;
}
char Enc::decode_char(char *result) {
    // Simply return the first element
    unsigned char *uresult = (unsigned char*) result;
    return (char) uresult[0];
}
unsigned char Enc::decode_uchar(char *result) {
    // Simply return the first element
    unsigned char *uresult = (unsigned char*) result;
    return uresult[0];
}

/* 16-bit */
void Enc::encode(char *result, short number) {
    // Encode the number big-endian
    unsigned char *uresult = (unsigned char*) result;
    uresult[0] = (number >> 8) & 0xFF;
    uresult[1] = number & 0xFF;
}
void Enc::encode(char *result, unsigned short number) {
    // Encode the number big-endian
    unsigned char *uresult = (unsigned char*) result;
    uresult[0] = (number >> 8) & 0xFF;
    uresult[1] = number & 0xFF;
}
short Enc::decode_short(char *result) {
    // Decode the given bytes with length 2
    unsigned char *uresult = (unsigned char*) result;
    short number = 0;
    number |= ((short) uresult[0]) << 8;
    number |= ((short) uresult[1]);
    return number;
}
unsigned short Enc::decode_ushort(char *result) {
    // Decode the given bytes with length 2
    unsigned char *uresult = (unsigned char*) result;
    unsigned short number = 0;
    number |= ((unsigned short) uresult[0]) << 8;
    number |= ((unsigned short) uresult[1]);
    return number;
}

/* 32-bit */
void Enc::encode(char *result, int number) {
    // Encode the number big-endian
    unsigned char *uresult = (unsigned char*) result;
    uresult[0] = (number >> 24) & 0xFF;
    uresult[1] = (number >> 16) & 0xFF;
    uresult[2] = (number >> 8) & 0xFF;
    uresult[3] = number & 0xFF;
}
void Enc::encode(char *result, unsigned int number) {
    // Encode the number big-endian
    unsigned char *uresult = (unsigned char*) result;
    uresult[0] = (number >> 24) & 0xFF;
    uresult[1] = (number >> 16) & 0xFF;
    uresult[2] = (number >> 8) & 0xFF;
    uresult[3] = number & 0xFF;
}
int Enc::decode_int(char *result) {
    // Decode the given bytes with length 4
    unsigned char *uresult = (unsigned char*) result;
    int number = 0;
    number |= ((int) uresult[0]) << 24;
    number |= ((int) uresult[1]) << 16;
    number |= ((int) uresult[2]) << 8;
    number |= ((int) uresult[3]);
    return number;
}
unsigned int Enc::decode_uint(char *result) {
    // Decode the given bytes with length 4
    unsigned char *uresult = (unsigned char*) result;
    unsigned int number = 0;
    number |= ((unsigned int) uresult[0]) << 24;
    number |= ((unsigned int) uresult[1]) << 16;
    number |= ((unsigned int) uresult[2]) << 8;
    number |= ((unsigned int) uresult[3]);
    return number;
}

/* 64-bit */
void Enc::encode(char *result, long number) {
    // Encode the number big-endian
    unsigned char *uresult = (unsigned char*) result;
    uresult[0] = (number >> 56) & 0xFF;
    uresult[1] = (number >> 48) & 0xFF;
    uresult[2] = (number >> 40) & 0xFF;
    uresult[3] = (number >> 32) & 0xFF;
    uresult[4] = (number >> 24) & 0xFF;
    uresult[5] = (number >> 16) & 0xFF;
    uresult[6] = (number >> 8) & 0xFF;
    uresult[7] = number & 0xFF;
}
void Enc::encode(char *result, unsigned long number) {
    // Encode the number big-endian
    unsigned char *uresult = (unsigned char*) result;
    uresult[0] = (number >> 56) & 0xFF;
    uresult[1] = (number >> 48) & 0xFF;
    uresult[2] = (number >> 40) & 0xFF;
    uresult[3] = (number >> 32) & 0xFF;
    uresult[4] = (number >> 24) & 0xFF;
    uresult[5] = (number >> 16) & 0xFF;
    uresult[6] = (number >> 8) & 0xFF;
    uresult[7] = number & 0xFF;
}
long Enc::decode_long(char *result) {
    // Decode the given bytes with length 8
    unsigned char *uresult = (unsigned char*) result;
    long number = 0;
    number |= ((long) uresult[0]) << 56;
    number |= ((long) uresult[1]) << 48;
    number |= ((long) uresult[2]) << 40;
    number |= ((long) uresult[3]) << 32;
    number |= ((long) uresult[4]) << 24;
    number |= ((long) uresult[5]) << 16;
    number |= ((long) uresult[6]) << 8;
    number |= ((long) uresult[7]);
    return number;
}
unsigned long Enc::decode_ulong(char *result) {
    // Decode the given bytes with length 8
    unsigned char *uresult = (unsigned char*) result;
    unsigned long number = 0;
    number |= ((unsigned long) uresult[0]) << 56;
    number |= ((unsigned long) uresult[1]) << 48;
    number |= ((unsigned long) uresult[2]) << 40;
    number |= ((unsigned long) uresult[3]) << 32;
    number |= ((unsigned long) uresult[4]) << 24;
    number |= ((unsigned long) uresult[5]) << 16;
    number |= ((unsigned long) uresult[6]) << 8;
    number |= ((unsigned long) uresult[7]);
    return number;
}
