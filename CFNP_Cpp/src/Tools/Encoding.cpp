/* ENCODING.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  DECRIPTION: This file contains all sorts of functions to parse multiple
*              bytes as other formats and back.
**/

#include "Encoding.h"

/* 8-bit */
void Enc::encode(char *result, char number) {
    // Simply set the first result to number
    result[0] = number;
}
void Enc::encode(char *result, unsigned char number) {
    // Simply set the first result to number
    result[0] = (char) number;
}
char Enc::decode_char(char *result) {
    // Simply return the first element
    return result[0];
}
unsigned char Enc::decode_uchar(char *result) {
    // Simply return the first element
    return (unsigned char) result[0];
}

/* 16-bit */
void Enc::encode(char *result, short number) {
    // Encode the number big-endian
    result[0] = (number >> 8) & 0xFF;
    result[1] = number & 0xFF;
}
void Enc::encode(char *result, unsigned short number) {
    // Encode the number big-endian
    result[0] = (number >> 8) & 0xFF;
    result[1] = number & 0xFF;
}
short Enc::decode_short(char *result) {
    // Decode the given bytes with length 2
    short number = 0;
    number |= ((short) result[0]) << 8;
    number |= ((short) result[1]);
    return number;
}
unsigned short Enc::decode_ushort(char *result) {
    // Decode the given bytes with length 2
    unsigned short number = 0;
    number |= ((unsigned short) result[0]) << 8;
    number |= ((unsigned short) result[1]);
    return number;
}

/* 32-bit */
void Enc::encode(char *result, int number) {
    // Encode the number big-endian
    result[0] = (number >> 24) & 0xFF;
    result[1] = (number >> 16) & 0xFF;
    result[2] = (number >> 8) & 0xFF;
    result[3] = number & 0xFF;
}
void Enc::encode(char *result, unsigned int number) {
    // Encode the number big-endian
    result[0] = (number >> 24) & 0xFF;
    result[1] = (number >> 16) & 0xFF;
    result[2] = (number >> 8) & 0xFF;
    result[3] = number & 0xFF;
}
int Enc::decode_int(char *result) {
    // Decode the given bytes with length 4
    int number = 0;
    number |= ((int) result[0]) << 24;
    number |= ((int) result[1]) << 16;
    number |= ((int) result[2]) << 8;
    number |= ((int) result[3]);
    return number;
}
unsigned int Enc::decode_uint(char *result) {
    // Decode the given bytes with length 4
    unsigned int number = 0;
    number |= ((unsigned int) result[0]) << 24;
    number |= ((unsigned int) result[1]) << 16;
    number |= ((unsigned int) result[2]) << 8;
    number |= ((unsigned int) result[3]);
    return number;
}

/* 64-bit */
void Enc::encode(char *result, long number) {
    // Encode the number big-endian
    result[0] = (number >> 56) & 0xFF;
    result[1] = (number >> 48) & 0xFF;
    result[2] = (number >> 40) & 0xFF;
    result[3] = (number >> 32) & 0xFF;
    result[4] = (number >> 24) & 0xFF;
    result[5] = (number >> 16) & 0xFF;
    result[6] = (number >> 8) & 0xFF;
    result[7] = number & 0xFF;
}
void Enc::encode(char *result, unsigned long number) {
    // Encode the number big-endian
    result[0] = (number >> 56) & 0xFF;
    result[1] = (number >> 48) & 0xFF;
    result[2] = (number >> 40) & 0xFF;
    result[3] = (number >> 32) & 0xFF;
    result[4] = (number >> 24) & 0xFF;
    result[5] = (number >> 16) & 0xFF;
    result[6] = (number >> 8) & 0xFF;
    result[7] = number & 0xFF;
}
long Enc::decode_long(char *result) {
    // Decode the given bytes with length 8
    long number = 0;
    number |= ((long) result[0]) << 56;
    number |= ((long) result[1]) << 48;
    number |= ((long) result[2]) << 40;
    number |= ((long) result[3]) << 32;
    number |= ((long) result[4]) << 24;
    number |= ((long) result[5]) << 16;
    number |= ((long) result[6]) << 8;
    number |= ((long) result[7]);
    return number;
}
unsigned long Enc::decode_ulong(char *result) {
    // Decode the given bytes with length 8
    unsigned long number = 0;
    number |= ((unsigned long) result[0]) << 56;
    number |= ((unsigned long) result[1]) << 48;
    number |= ((unsigned long) result[2]) << 40;
    number |= ((unsigned long) result[3]) << 32;
    number |= ((unsigned long) result[4]) << 24;
    number |= ((unsigned long) result[5]) << 16;
    number |= ((unsigned long) result[6]) << 8;
    number |= ((unsigned long) result[7]);
    return number;
}
