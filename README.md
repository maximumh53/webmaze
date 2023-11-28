# Netmaze + Webmaze


### **Netmaze**
- python program intended to facilitate and run on the Netmaze protocol, completing all tasks before exiting the maze
- encoded with UTF-8
- messages sent with TCP transport protocol
    - framed with newline character '\n'


#### Message Types
- query {port}
    - sent by server to client
    - establishes a new connection to the server at the specified TCP port if such a connection does not exist
    - send a new identification message to an existing connection to the specified port
- id {user}
    - sent by clients to server
    - sent whenever the client establishes a new connection (case 1 above) or is requested by the server (case 2 above)
- status {message}
    - sent by server to client
    - following query messages will eventually result in a success message
- listen {port}
    - sent by client to server
    - requests that client opens a new socket for receiving connections on the specific TCP port
    - server may send multiple query messages on connect before client receives a status success message, exiting the maze

### **Webmaze**
- implemetnation of a client-server pair using remote procedure calls(RPCs) through a REST interface
- Web server + client for execution of Netmaze client and report stats
    - client program - REST requests
    - server program - responds to client requests

#### **Server** 

#### REST Requests
- POST /api/run/{id}
    - run netmaze client with given id
- GET /api/queries?run={runId}&limit={count}&start={index}
    - retrieve page of queries related to given runID
    - implements pagination
- GET /api/list?limit={count}&start={index}
    - retrieve page of completed runs
    - implements pagination
est

#### Error Handling
- HTTP 204: No Content
    - request arriving before netmaze finishes running
- HTTP 400: Bad Request
    - requested limit larger than 30

#### **Client** 
- implementation of command-line program to issue REST requests toward server
- cannot use libraries to handle HTTP requests
- supports
    - submitting new run request receiving id from command line and calling /api/run endpoint
    - getting a list of completed run identifiers from the server using the /api/list endpoint
    - compute the mean and variance of the number of queries across all completed NetMaze runs on the server by combining the /api/list and /api/queries endpoints.

### **Implementation**
- Server
    - uuid - generate unique runids
    - asyncio - creation of new connections and handling of listen messages
    - Flask - utilized the Flask microframework to handle REST requests
- Client
    - argparse - implementation from cli
    - socket - sending requests, receiving responses
    - json - handling messages
    - time - implementing slight delays
    - statistics - calculation


Netmaze is a Python program designed to operate on the Netmaze protocol, where it performs various tasks before exiting a maze. It uses UTF-8 encoding, sends messages over TCP with newline framing, and has distinct message types like 'query', 'id', 'status', and 'listen' for communication between server and client. In contrast, Webmaze is a client-server implementation using remote procedure calls (RPCs) via a REST interface. The server handles REST requests like running Netmaze clients, retrieving query pages, and listing completed runs, with specific HTTP error handling. The client is a command-line program that issues REST requests to the server, managing tasks such as submitting run requests, listing completed runs, and computing statistical data from these runs. The server employs uuid for unique identifiers, asyncio for connection management, and Flask for REST requests. The client uses argparse for command-line interface, socket and json for communication, time for delays, and statistics for data analysis.








#
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
