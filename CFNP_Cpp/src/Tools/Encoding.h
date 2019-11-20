/* ENCODING.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  DECRIPTION: This file contains all sorts of functions to parse multiple
*              bytes as other formats and back.
**/

#ifndef ENCODING_H
#define ENCODING_H

namespace Enc {
    /* Encodes given 8-bit number as byte array (big-endian) */
    void encode(char *result, char number);
    /* Encodes given unsigned 8-bit number as byte array (big-endian) */
    void encode(char *result, unsigned char number);
    /* Encodes given 16-bit number as byte array (big-endian) */
    void encode(char *result, short number);
    /* Encodes given unsigned 16-bit number as byte array (big-endian) */
    void encode(char *result, unsigned short number);
    /* Encodes given 32-bit number as byte array (big-endian) */
    void encode(char *result, int number);
    /* Encodes given unsigned 32-bit number as byte array (big-endian) */
    void encode(char *result, unsigned int number);
    /* Encodes given 64-bit number as byte array (big-endian) */
    void encode(char *result, long number);
    /* Encodes given unsigned 64-bit number as byte array (big-endian) */
    void encode(char *result, unsigned long number);

    /* Decodes gives byte array as a 8-bit char */
    char decode_char(char *result);
    /* Decodes given byte array as an unsigned 8-bit char */
    unsigned char decode_uchar(char *result);
    /* Decodes gives byte array as a 16-bit char */
    short decode_short(char *result);
    /* Decodes given byte array as an unsigned 16-bit char */
    unsigned short decode_ushort(char *result);
    /* Decodes gives byte array as a 32-bit char */
    int decode_int(char *result);
    /* Decodes given byte array as an unsigned 32-bit char */
    unsigned int decode_uint(char *result);
    /* Decodes gives byte array as a 64-bit char */
    long decode_long(char *result);
    /* Decodes given byte array as an unsigned 64-bit char */
    unsigned long decode_ulong(char *result);
}

#endif