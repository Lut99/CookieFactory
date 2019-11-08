/* TEST.c
 *   by tHE iNCREDIBLE mACHINE
 * 
 * DESCRIPTION: Test file for both Encoding and Message
 */

#include <stdlib.h>
#include <stdio.h>
#include "Encoding.h"
#include "Message.h"

void print_string(char* s) {
    char c = s[0];
    int i = 0;
    printf("'");
    while (c != '\0') {
        printf("%c", c);
        c = s[i];
        i += 1;
    }
    printf("'\n");
}

void print_bytes(unsigned char* bytes, int length) {
    int i;
    printf("[");
    for (i = 0; i < length; i++) {
        if (i > 0) {
            printf(",");
        }
        printf("%x", bytes[i]);
    }
    printf("]\n");
}

void print_connectionrequest(ConnectionRequest *msg) {
    printf("ConnectionRequest:\n");
    printf("  -> subcode: %u\n", msg->base.subcode);
    printf("  -> opcode: %u\n", msg->base.opcode);
    printf("  -> password: ");
    if (msg->password == NULL) {
        printf("NULL\n");
    } else {
        print_string(msg->password);
    }
    printf("  -> raw: ");
    if (msg->base.raw == NULL) {
        printf("NULL\n");
    } else {
        print_bytes(msg->base.raw, msg->base.raw_length);
    }
}

void test_encoding() {
    printf("\n# Testing Encoding.c #\n");
    // For each type, create a random number and print it
    unsigned short t1 = 300;
    unsigned char *raw_t1 = malloc(2 * sizeof(unsigned char));
    printf("Source: %u\n", t1);
    encode_uint16(t1, raw_t1);
    print_bytes(raw_t1, 2);
    unsigned short t1_back = decode_uint16(raw_t1);
    printf("Result: %u\n", t1_back);
    free(raw_t1);

    unsigned int t2 = 70000125;
    unsigned char *raw_t2 = malloc(4 * sizeof(unsigned char));
    printf("Source: %u\n", t2);
    encode_uint32(t2, raw_t2);
    print_bytes(raw_t2, 4);
    unsigned int t2_back = decode_uint32(raw_t2);
    printf("Result: %u\n", t2_back);
    free(raw_t2);

    unsigned long t3 = 20132413001524;
    unsigned char *raw_t3 = malloc(8 * sizeof(unsigned char));
    printf("Source: %lu\n", t3);
    encode_uint64(t3, raw_t3);
    print_bytes(raw_t3, 8);
    unsigned long t3_back = decode_uint64(raw_t3);
    printf("Result: %lu\n", t3_back);
    free(raw_t3);
}

void test_message_ums() {
    printf("\n# Testing Message.c - Unified Message Structure #\n");
    // Create a sample message
    unsigned char *msg = malloc(18 * sizeof(unsigned char));
    char i;
    for (i = 0; i < 9; i++) {
        msg[i + 8] = i + '0';
    }
    msg[17] = '\0';
    // Create a header with the information
    Header *h = malloc(sizeof(Header));
    h->subcode = 42;
    h->opcode = 43;
    h->length = 10;
    h->next_up = 3;
    printf("Header (source):\n");
    printf("  ->subcode: %u\n", h->subcode);
    printf("  ->opcode: %u\n", h->opcode);
    printf("  ->length: %u\n", h->length);
    printf("  ->next_up: %u\n", h->next_up);
    printf("Message (source):\n  ");
    print_string(msg + 8);
    // Encapsulate that header
    encapsulate(h, msg + 8, msg);
    // Print the byte stream
    printf("Bytes (encapsulated):\n  ");
    print_bytes(msg, 18);
    // Parse back the header
    Header *h_back = malloc(sizeof(Header));
    decapsulate(h_back, msg);
    // Print the parsed results
    printf("Header (parsed):\n");
    printf("  ->subcode: %u\n", h_back->subcode);
    printf("  ->opcode: %u\n", h_back->opcode);
    printf("  ->length: %u\n", h_back->length);
    printf("  ->next_up: %u\n", h_back->next_up);
    printf("Message (parsed):\n  ");
    print_string(msg + 8);

    // Free everything
    free(msg);
    free(h);
    free(h_back);
}

void test_message_connectionrequest() {
    printf("\n# Testing Message.c - ConnectionRequest #\n");
    // Create the object and store a password
    ConnectionRequest *c = create_connection_request();
    c->password = "1234567890";
    c->password_length = 10;
    printf("Source:\n");
    print_connectionrequest(c);
    // Parse the connectionrequest, and the show the parsed result
    pack_connection_request(c);
    printf("Packed: ");
    print_connectionrequest(c);
    ConnectionRequest *c_back = create_connection_request();
    parse_connection_request(c_back, c->base.raw, c->base.raw_length);
    printf("Parsed:\n");
    print_connectionrequest(c_back);

    // Free it all
    free_connection_request(c);
    free_connection_request(c_back);
}

int main() {
    printf("*** test.c ***\n");
    printf("Word sizes:\n");
    printf("  - char: %lu bytes\n", sizeof(unsigned char));
    printf("  - short: %lu bytes\n", sizeof(unsigned short));
    printf("  - int: %lu bytes\n", sizeof(unsigned int));
    printf("  - long: %lu bytes\n", sizeof(unsigned long));
    // First, test the encoding
    test_encoding();
    // Then the message UFS
    test_message_ums();
    // Test the message's ConnectionRequest functions
    test_message_connectionrequest();
    return 0;
}