import argparse, socket, json, time, statistics

# requests: 
# submit new run request with id from command line /api/run
# list of complete run identifiers
# mean and varience of number of queries

def read_line(r):
    time.sleep(0.1)
    line=r.recv(4096).decode()
    #print(line)
    flag = False
    msg=""
    count = 0
    for char in line:
        if char=='{':
            count+=1
            flag = True
        if flag: msg+=char
        if char=="}":
            count-=1
            if count==0: return msg 

def get_runs():
    runs=[]
    next=f"/api/list?limit=1&start=1" #first
    while next != None:
        s=socket.socket()
        s.connect(("localhost",5000))
        msg=f"GET {next} HTTP/1.1\r\n\r\n"
        s.send(msg.encode())
        #print("request sent")
        holder = read_line(s)
        if holder != None:
            holder=json.loads(holder)
            next=holder["next"]
            runIDs=holder["runIds"]
            try:
                runs.append(runIDs[0])
            except: return "No Runs Recorded"
        s.close()
    return runs

def numqueries(runID):
    limit, start =1, 1
    count=0
    next=f"/api/queries?run={runID}&limit={limit}&start={start}"
    while (next!= None): #next = None, reached end
        s=socket.socket()
        s.connect(("localhost",5000))
        s.send(f"GET {next} HTTP/1.1\r\n\r\n".encode())
        #print("request sent")
        holder=read_line(s)
        box=json.loads(holder)
        next=box["next"]
        start+=1
        count+=1
        s.close()
    print(f"Number of queries for {runID}: {count}")
    return count

def stats():
    totalruns = get_runs()
    nums = [numqueries(run) for run in totalruns]
    mean = statistics.mean(nums)
    var = statistics.variance(nums, mean)
    return mean, var

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "REST client for NetMaze server")
    parser.add_argument("action", choices=["submit", "list", "stats"], help="action to perform: submit, list, stats")
    parser.add_argument("--id", help="run id (required for submit)")
    args = parser.parse_args()

    if args.action == "submit":
        if not args.id:
            print("Error: run id required for submit action")
        msg=f"GET /api/run/{args.id} HTTP/1.1\r\n\r\n"
        s = socket.socket()
        s.connect(("127.0.0.1", 5000))
        s.send(msg.encode())
        print("request sent")
        ret=read_line(s)
        s.close()
        print(ret)
    elif args.action == "list":
        print(get_runs())
    elif args.action == "stats":
        mean, variance = stats()
        print(f"mean = {mean}, varience = {variance}")