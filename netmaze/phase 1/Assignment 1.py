#!/usr/bin/env python3

import socket

prev = []
sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(51)]

def read_line(r: socket.SocketType) -> str:
    sentinel = "\n".encode(encoding="ascii")

    if r.recv(1, socket.MSG_PEEK) == ''.encode(encoding="ascii"):
        return "finish"
    buf = r.recv(1) #socket closed when trying to read
    while buf[-1] != sentinel[0]:
        buf += r.recv(1)
        #print(buf)
    line = buf.decode("ascii")
    return line

sockets[0].connect(("67.159.95.167", 51300))
sockets[0].send("id mqh5\n".encode(encoding="ascii"))
line = read_line(sockets[0])

#listening for message on last port, primary port
#at exit of the maze

while line[0] == 'q':
    second = int(line.split()[1])
    if second not in prev:
        sockets[second - 51300].connect(("67.159.95.167", second))
        prev.append(second)
    #print(second)
    sockets[second - 51300].send("id mqh5\n".encode(encoding="ascii"))
    line = read_line(sockets[second - 51300])
    #print(line)

print(line)

line = read_line(sockets[0])
msg = line.strip()
print(msg.split()[0])
print(f"received: {msg}")
