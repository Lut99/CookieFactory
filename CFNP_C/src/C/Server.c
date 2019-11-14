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

#define MAX_CONNECTIONS 5

/* SERVER THREAD */

void *server_thread(void *args) {
    CFNPServer *server = (CFNPServer *) args;
    int i, n_connections;
    int *sockets[MAX_CONNECTIONS + 1];
    CFNPConnection connections[MAX_CONNECTIONS];

    // Init some variables
    sockets[0] = server->sock;
    n_connections = 0;

    // Run while we can
    while (server->t_status == THREAD_RUNNING) {
        // Wait until any of the sockets becomes available
        // TODO: Use select() to handle new connections and read from old ones
    }

    // Cleanup any socket(s)
    for (i = 0; i < n_connections; i++) {
        close(connections[i].sock);
    }
}

/* SERVER OPERATIONS */

int server_init(CFNPServer *server, unsigned short port) {
    int i;

    server = malloc(sizeof(CFNPServer));

    // Try to create the socket
    server->sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server->sock < 0) {
        // Dealloc
        free(server);
        return SOCK_CREATE_ERR;
    }

    // Assign address fields for the server
    server->addr.sin_family = AF_INET;
    server->addr.sin_port = htons(port);
    server->addr.sin_addr.s_addr = INADDR_ANY;

    // Attempt to bind this address to the socket
    if (bind(server->sock, (struct sockaddr *) server->addr, sizeof(server->addr)) < 0) {
        // Dealloc, since we didn't make it
        free(server);
        return SOCK_BIND_ERR;
    }

    // Set the server to listen
    listen(server->sock, MAX_CONNECTIONS);

    // Now that we successfully created the socket, create the thread
    server->t_status = THREAD_RUNNING;
    pthread_create(&server->t_id, NULL, server_thread, (void *) server);

    // Done
    return SOCK_SUCCES;
}

void server_destroy(CFNPServer *server) {
    // Set the server's flag to THREAD_STOPPED
    server->t_status = THREAD_STOPPED;

    // Wait until the server's thread has joined
    pthread_join(&server->t_id, NULL);

    // Dealloc server
    close(server->sock);
    free(server);
}

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