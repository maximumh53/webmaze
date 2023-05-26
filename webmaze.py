import uuid, asyncio
from flask import Flask, request

app = Flask(__name__)

querystorage = {}
recruns = []
running = False

#POST /api/run/{id}
@app.route('/api/run/<string:id>', methods = ['GET','POST'])
def run(id):
    global running, recruns
    if running == True: return "Error 204: No Content"
    running = True
    runID = str(uuid.uuid4())
    
    queries = []
    def run_netmaze():
        send = "id " + id + "\n"
        sec, locks, readers, writers = {}, {}, {}, {}
        tasks = [] #list of all tasks
        for i in range(51301, 51351): #one lock for each port
            locks[i] = asyncio.Lock()

        async def query1(port):
            port = int(port)
            #global sec, readers, writers, locks, id
            #start = time.time()
            async with locks[port]:
                if port not in sec.keys():
                    sec[port] = [None]*2
                    readers[port],writers[port] = await asyncio.open_connection("67.159.95.167", port)
                writers[port].write(send.encode(encoding="ascii"))
                buf = await readers[port].readline() 
            #print(time.time() - start)
            if len(buf) != 0: queries.append({"connection_source": "client", "connection_port": port, "query_target": buf.decode("ascii").split()[1]}) 
            return buf.decode("ascii").strip()

        async def handler(reader, writer, port):
            while True:
                new = await reader.readline()
                queries.append({"connection_source": "server", "connection_port": port, "query_target": new.decode("ascii").split()[1]})
                tasks.append(asyncio.create_task(query(new.decode("ascii"), port)))

        async def listen(port):
            server = await asyncio.start_server(lambda r, w: handler(r, w, port), host='0.0.0.0', port=port)
            await server.serve_forever()

        async def query(msg: str, curr: int): #first queryn of each thread
            #print("msg " + msg)
            action, port1 = msg.strip().split()
            port = int(port1)
            #queries.append(port)
            #print(port)
            queries.append({"connection_source": "client", "connection_port": curr, "query_target": port})
            while action == "query":
                nxt = await query1(port)
                if len(nxt) == 0: return
                #print("nxt: " + nxt)
                action, port = nxt.split()[0], int(nxt.split()[1])
                #print(port)
                #queries.append(port)
            #print("listen port " + str(port))
            tasks.append(asyncio.create_task(listen(port)))

        async def main():
            #primary connection
            reader, writer = await asyncio.open_connection("67.159.95.167", 51300)
            writer.write(send.encode(encoding="ascii"))
            await writer.drain()
            buf = await reader.readline()
            tasks.append(asyncio.create_task(query(buf.decode("ascii"), 51300)))
            status = await reader.readline()
            message = status.decode("ascii")
            print(f"received: {message}")
            return message
        
        x = asyncio.run(main())
        return x
        #print("netmazeid" +netmaze.id)
    
    stat = run_netmaze()
    running = False
    if stat != "status success\n": return "Error 404: Not Found"
    
    print(len(queries))
    recruns.append(runID)
    querystorage[runID] = queries
    #only update if success
    print(querystorage)
    print(recruns)
    return {"runID": runID}

#GET /api/queries?run={runId}&limit={count}&start={index}
@app.route('/api/queries', methods = ['GET'])
def retqueries2(): #retrieve queries
    #assume a start of 1 is a start of first(0) element
    args = request.args
    print(args.to_dict())
    runID = args.get("run", type = str, default = "")
    limit = args.get("limit", type = int, default = 1)
    start = args.get("start", type = int, default = 1)
    if limit > 30: return "Error 400: Not Found"
    print(runID)
    print(limit)
    print(start)

    data = querystorage[runID]
    print(data)
    size = len(data)
    data = data[(start - 1):(start + limit - 1)] # spliced data
    print(data)

    if start == 1: prev = None
    elif start - limit < 1: #edge
        pstart = 1
        plim = start - 1
        prev = f"/api/queries?run={runID}&limit={plim}&start={pstart}"
    else: #general
        pstart = start - limit
        plim = limit
        prev = f"/api/queries?run={runID}&limit={plim}&start={pstart}"

    if start + limit - 1 == size:
        next = None
    elif (start+2*limit-1) > size: #edge
        nstart = start + limit
        nlim = limit - nstart + 1
        next = f"/api/queries?run={runID}&limit={nlim}&start={nstart}"
    else: #general
        nstart = start + limit
        nlim = limit
        next = f"/api/queries?run={runID}&limit={nlim}&start={nstart}"

    return {"runId": runID,
            "limit": limit,
            "start": start,
            "queries": data,
            "prev": prev,
            "next": next
           }

#GET /api/list?limit={count}&start={index}
@app.route('/api/list', methods = ['GET'])
def getruns():
    global recruns
    args = request.args
    limit = args.get("limit", type = int, default = 1)
    start = args.get("start", type = int, default= 1)

    if limit > 30: return "Error 400: Not Found"

    print(recruns)
    data = recruns
    print(data)
    size = len(data)

    data = recruns[(start - 1):(start + limit - 1)] # spliced data

    if start == 1: prev = None
    elif start - limit < 1: #edge
        pstart = 1
        plim = start - 1
        prev = f"/api/list?limit={plim}&start={pstart}"
    else: #general
        pstart = start - limit
        plim = limit
        prev = f"/api/list?limit={plim}&start={pstart}"

    if start + limit - 1 == size:
        next = None
    elif (start+2*limit-1) > size: #edge
        nstart = start + limit
        nlim = limit - nstart + 1
        next = f"/api/list?limit={nlim}&start={nstart}"
    else: #general
        nstart = start + limit
        nlim = limit
        next = f"/api/list?limit={nlim}&start={nstart}"

    print(data)

    return {
        "limit": limit,
        "start": start,
        "runIds": data,
        "prev": prev,
        "next": next
    }
    
if __name__ == '__main__':
    app.run()