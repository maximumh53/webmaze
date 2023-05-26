import asyncio

id = ""
sec, locks, readers, writers = {}, {}, {}, {}
tasks = [] #list of all tasks
for i in range(51301, 51351): #one lock for each port
    locks[i] = asyncio.Lock()

async def query1(port):
    port = int(port)
    global sec, readers, writers, locks, id
    async with locks[port]:
        if port not in sec.keys():
            sec[port] = [None]*2
            readers[port],writers[port] = await asyncio.open_connection("67.159.95.167", port)
        writers[port].write(id.encode(encoding="ascii"))
        buf = await readers[port].readline() 
    if len(buf) != 0: print({"connection_source": "client", "connection_port": port, "query_target": buf.decode("ascii").split()[1]})
    return buf.decode("ascii").strip()


async def handler(reader, writer, port):
    while True:
        new = await reader.readline()
        print({"connection_source": "server", "connection_port": port, "query_target": new.decode("ascii").split()[1]})
        tasks.append(asyncio.create_task(query(new.decode("ascii"), port)))

async def listen(port):
    server = await asyncio.start_server(lambda r, w: handler(r, w, port), host='0.0.0.0', port=port)
    await server.serve_forever()

async def query(msg: str, curr: int): #first queryn of each thread
    #print("msg " + msg)
    action, port1 = msg.strip().split()
    port = int(port1)
    #print(port)
    print({"connection_source": "client", "connection_port": curr, "query_target": port})
    while action == "query":
        nxt = await query1(port)
        if len(nxt) == 0: return
        #print("nxt: " + nxt)
        #print(port)
        action, port = nxt.split()[0], int(nxt.split()[1])
        #print(port)
    #print("listen port " + str(port))
    tasks.append(asyncio.create_task(listen(port)))

async def main():
    #primary connection
    reader, writer = await asyncio.open_connection("67.159.95.167", 51300)
    writer.write(id.encode(encoding="ascii"))
    buf = await reader.readline()
    #print({"connection_source": "client", "connection_port": 51300, "query_target": buf.decode("ascii").split()[1]})
    tasks.append(asyncio.create_task(query(buf.decode("ascii"), 51300)))
    status = await reader.readline()
    message = status.decode("ascii")
    print(f"received: {message}")
    return

def run(identifier):
    global id
    id = "id " + identifier + "\n"
    asyncio.run(main())

run("mqh5")