/* ENCODING.h
 *   by tHE iNCREDIBLE mACHINE
 *
 * DECRIPTION: This file contains all headers for ENCODING.c
 */

/* Makes sure the header is only run once */
#ifndef ENCODING_H_
#define ENCODING_H_

/* Takes a byte array and tries to parse the first two bytes as a short */
unsigned short decode_uint16(unsigned char* bytes);
/* Takes a byte array and tries to parse the first four bytes as an int */
unsigned int decode_uint32(unsigned char* bytes);
/* Takes a byte array and tries to parse the first eight bytes as a long */
unsigned long decode_uint64(unsigned char* bytes);

/* Takes a short, and converts that to a byte array of length 2. That array
   is inserted at the result pointer location. */
void encode_uint16(unsigned short number, unsigned char* result);
/* Takes an int, and converts that to a byte array of length 4. That array
   is inserted at the result pointer location. */
void encode_uint32(unsigned int number, unsigned char* result);
/* Takes a long, and converts that to a byte array of length 8. That array
   is inserted at the result pointer location. */
void encode_uint64(unsigned long number, unsigned char* result);

#endif