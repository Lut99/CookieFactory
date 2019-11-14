/* SERVER.h
 *   by tHE iNCREDIBLE mACHINE
 * 
 * DECRIPTION: Header file for Server.c.
 */

/* Makes sure the header is only run once */
#ifndef MESSAGE_H_
#define MESSAGE_H_

// Include stuff for sockest
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <pthread.h>

// Error codes
#define SOCK_SUCCES 0
#define SOCK_CREATE_ERR -1
#define SOCK_BIND_ERR -2

// Thread statusses
#define THREAD_RUNNING = 1
#define THREAD_STOPPED = 0

typedef struct {
    int sock;
    struct sockaddr_in addr;
    pthread_t t_id;
    int t_status;
} CFNPServer;

typedef struct {
    int sock;
    struct sockaddr_in addr;
} CFNPConnection;

/* SERVER OPERATIONS */

/* Creates and starts a server thread and returns a server instance. */
int server_init(CFNPServer *server);
/* Stops the server thread and destroys the server instance */
void server_destroy(CFNPServer *server);

#endif