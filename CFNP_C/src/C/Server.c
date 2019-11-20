/* SERVER.c
 *   by tHE iNCREDIBLE mACHINE
 *
 * DECRIPTION: This file contains the logic for a CFNP server. Uses the
 *             messages from Tools/Messages.c.
 */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/select.h>

#include "Server.h"

#define MAX_CONNECTIONS 5
#define BUFFER_SIZE 65541 // 65535 + 6 for the header

/* SERVER THREAD */
void *server_thread(void *args) {
    /* Declare local variables */
    int i, n_connections;
    int sockets[MAX_CONNECTIONS + 1];
    char buffer[BUFFER_SIZE];
    CFNPConnection connections[MAX_CONNECTIONS];
    fd_set *readable_sockets;

    // Cast the arguments
    CFNPServer *server = (CFNPServer *) args;

    // Init some variables
    sockets[0] = server->sock;
    n_connections = 0;
    FD_ZERO(readable_sockets);

    // Add the server socket to the list of readable sockets
    FD_SET(server->sock, readable_sockets);

    if (server->verbose) {
        printf("[CFNPServer] Initialized\n");
    }

    // Run while we can
    while (server->t_status == THREAD_RUNNING) {
        // Prepare the list of sockets that have to be readable
        FD_ZERO(readable_sockets);
        FD_SET(server->sock, readable_sockets);
        for (i = 0; i < n_connections; i++) {
            FD_SET(connections[i].sock, readable_sockets);
        }
        // Wait until any of them is readable
        int readable = select(MAX_CONNECTIONS, readable_sockets, NULL, NULL, NULL);
        if (readable < 0) {
            server->t_error = THREAD_SELECT_ERR;
            break;
        }

        // First, check if the server has a pending accept
        if (FD_ISSET(server->sock, readable)) {
            // New connection incoming
            CFNPConnection conn;
            conn.sock = accept(server->sock, (struct sockaddr *) &conn.addr, sizeof(conn.addr));
            if (conn.sock < 0) {
                // Something bad has happened
                if (server->verbose) {
                    printf("[CFNPServer] Could not accept new connection: error\n");
                }
                server->t_error = SOCK_ACCEPT_ERR;
                break;
            }
            // Make sure we can accomodate it
            if (n_connections + 1 >= MAX_CONNECTIONS) {
                // We can't, drop it
                close(conn.sock);
                if (server->verbose) {
                    printf("[CFNPServer] Could not accept new connection: too many connections\n");
                }
            } else {
                // We can, store it
                conn.status = CONN_PENDING;
                connections[n_connections] = conn;
                n_connections++;
                if (server->verbose) {
                    printf("[CFNPServer] Accepted new connection as connection %i\n", n_connections);
                }
            }
        }
        // Then, check for the individual connections themselves
        for (i = 0; i < readable; i++) {
            CFNPConnection conn = connections[i];
            if (FD_ISSET(conn.sock, readable)) {
                // This connection send us data, so read it
                int n_read = read(conn.sock, buffer, BUFFER_SIZE);
                if (n_read < 0) {
                    // Could not read from this connection, so stop it
                    
                }
            }
        }
    }

    // Cleanup any socket(s)
    for (i = 0; i < n_connections; i++) {
        close(connections[i].sock);
    }

    return NULL;
}

/* SERVER OPERATIONS */

int server_init(CFNPServer *server, unsigned short port, int is_verbose) {
    int i;

    // Initialize the server struct
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
    if (bind(server->sock, (struct sockaddr *) &server->addr, sizeof(server->addr)) < 0) {
        // Dealloc, since we didn't make it
        free(server);
        return SOCK_BIND_ERR;
    }

    // Set the server to listen
    listen(server->sock, MAX_CONNECTIONS);

    // Now that we successfully created the socket, create the thread
    server->verbose = is_verbose;
    server->t_status = THREAD_RUNNING;
    server->t_error = THREAD_SUCCESS;
    pthread_create(&server->t_id, NULL, server_thread, (void *) server);

    // Done
    return SOCK_SUCCES;
}
void server_destroy(CFNPServer *server) {
    // Set the server's flag to THREAD_STOPPED
    server->t_status = THREAD_STOPPED;

    // Wait until the server's thread has joined
    pthread_join(server->t_id, NULL);

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