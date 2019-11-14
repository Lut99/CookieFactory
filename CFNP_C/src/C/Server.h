/* SERVER.h
 *   by tHE iNCREDIBLE mACHINE
 * 
 * DECRIPTION: Header file for Server.c.
 */

/* Makes sure the header is only run once */
#ifndef SERVER_H_
#define SERVER_H_

// Include stuff for sockets
#include <netinet/in.h>
#include <pthread.h>
#include "Tools/Message.h"

// Error codes
#define SOCK_SUCCES 0
#define SOCK_CREATE_ERR -1
#define SOCK_BIND_ERR -2
#define SOCK_ACCEPT_ERR -3

// Connection statusses
#define CONN_PENDING 0
#define CONN_ACCEPTED 1

// Thread statusses
#define THREAD_RUNNING 1
#define THREAD_STOPPED 0
// Thread errors
#define THREAD_SUCCESS 0
#define THREAD_SELECT_ERR -1

typedef struct {
    int sock;
    struct sockaddr_in addr;
    pthread_t t_id;
    int t_status;
    int t_error;
    Message *inbox;
} CFNPServer;

typedef struct {
    int sock;
    struct sockaddr_in addr;
    int status;
} CFNPConnection;

/* SERVER OPERATIONS */

/* Creates and starts a server thread and returns a server instance. */
int server_init(CFNPServer *server, unsigned short port);
/* Stops the server thread and destroys the server instance */
void server_destroy(CFNPServer *server);

#endif