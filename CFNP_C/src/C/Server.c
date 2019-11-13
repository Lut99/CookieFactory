/* SERVER.c
 *   by tHE iNCREDIBLE mACHINE
 *
 * DECRIPTION: This file contains the logic for a CFNP server. Uses the
 *             messages from Tools/Messages.c.
 */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include "Server.h"
#include "Tools/Message.h"

// Include stuff for sockest
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main() {
    // Init some variables
    int sockfd, newsockfd, portno, clilen, n;
    char buffer[256];
    struct sockaddr_in serv_addr, cli_addr;

    // Create the socket object
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Could not create a socket\n");
        exit(1);
    }

    // Set the address to zero
    portno = 8080;

    // Fill in the serv_addr struct
    serv_addr.sin_family = AF_INET;
    // Tip: htons converts to network endian
    serv_addr.sin_port = htons(portno);
    serv_addr.sin_addr.s_addr = INADDR_ANY;

    // Try to bind the given address to the server socket
    if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
        perror("Could not bind socket to port\n");
        exit(1);
    }

    // Let the server listen (max 5 clients)
    listen(sockfd, 5);

    // Wait until someone accepted the connection
    clilen = sizeof(cli_addr);
    newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
    if (newsockfd < 0) {
        perror("Could not accept client\n");
        exit(1);
    }

    // Read what the client sends us
    // n is how many characters are read
    n = read(newsockfd, buffer, 255);
    if (n < 0) {
        perror("Could not read socket message from client\n");
        exit(1);
    }
    printf("Received message: %s\n", buffer);
    n = write(newsockfd, "I got your message", 18);
    if (n < 0) {
        perror("Could not send message back to client\n");
    }

    close(newsockfd);
    close(sockfd);

    exit(0);
}