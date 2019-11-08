/* ENCODING.c
 *   by tHE iNCREDIBLE mACHINE
 *
 * DECRIPTION: This file contains all sorts of functions to parse multiple
 *             bytes as other formats.
 */

#include <limits.h>
#include <stdio.h>
#include "Encoding.h"

unsigned short decode_uint16(unsigned char* bytes) {
    /* Decodes given byte array (of length 2) as a 16-bit integer */
    unsigned short result = 0;
    char i;
    char i_neg = 8;
    for (i = 0; i < 2; i++) {
        result |= ((unsigned short) bytes[i])  << i_neg;
        i_neg -= 8;
    }
    return result;
}
unsigned int decode_uint32(unsigned char* bytes) {
    /* Decodes given byte array (of length 4) as a 32-bit integer */
    unsigned int result = 0;
    char i;
    char i_neg = 24;
    for (i = 0; i < 4; i++) {
        result |= ((unsigned int) bytes[i]) << i_neg;
        i_neg -= 8;
    }
    return result;
}
unsigned long decode_uint64(unsigned char* bytes) {
    /* Decodes given byte array (of length 8) as a 64-bit integer */
    unsigned long result = 0;
    char i;
    char i_neg = 56;
    for (i = 0; i < 8; i++) {
        result |= ((unsigned long) bytes[i])  << i_neg;
        i_neg -= 8;
    }
    return result;
}

void encode_uint16(unsigned short number, unsigned char* result) {
    /* Encodes given number into a 2-byte char array. The result is put in the
     * result pointer */
    char i;
    char i_neg = 8;
    for (i = 0; i < 2; i++) {
        result[i] = (number >> i_neg) & 0xFF;
        i_neg -= 8;
    }
}
void encode_uint32(unsigned int number, unsigned char* result) {
    /* Encodes given number into a 4-byte char array. The result is put in the
     * result pointer */
    char i;
    char i_neg = 24;
    for (i = 0; i < 4; i++) {
        result[i] = (number >> i_neg) & 0xFF;
        i_neg -= 8;
    }
}
void encode_uint64(unsigned long number, unsigned char* result) {
    /* Encodes given number into a 8-byte char array. The result is put in the
     * result pointer */
    char i;
    char i_neg = 56;
    for (i = 0; i < 8; i++) {
        result[i] = (number >> i_neg) & 0xFF;
        i_neg -= 8;
    }
}