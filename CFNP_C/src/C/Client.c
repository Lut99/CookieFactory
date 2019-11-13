/* CLIENT.c
 *   by tHE iNCREDIBLE mACHINE
 *
 * DECRIPTION: This file contains all logic for a client for the CFNP. Uses
 *             messages from Tools/Message.c.
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "Client.h"
#include "Tools/Message.h"

// Include socket related things
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <arpa/inet.h>

int main () {
    int sockfd, portno, n;
    struct sockaddr_in serv_addr;

    char buffer[256];
    portno = 8080;
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Could not create a socket\n");
        exit(1);
    }

    // Fill the serv_addr struct
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(portno);

    // Try to connect to the given server
    if (connect(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
        perror("Could not connect to server\n");
        exit(1);
    }

    // Query a message, send it to the server, then read a response
    n = write(sockfd, "Hello there!", strlen("Hello there!"));
    if (n < 0) {
        perror("Could not write to server");
        exit(1);
    }
    n = read(sockfd, buffer, 255);
    if (n < 0) {
        perror("Could not read from server");
    }
    printf("%s\n", buffer);
    
    // Close the sockets
    close(sockfd);

    exit(0);
}