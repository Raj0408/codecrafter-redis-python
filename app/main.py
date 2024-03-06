# Uncomment this to pass the first stage
import socket
import threading
import time
import argparse
from enum import Enum, auto
import sys


myTime = time.time_ns()
myDict = {}
flag = False

DEFAULT_PORT = 6379
CRFL = "\r\n"
MASTER_HOST = None 
MASTER_PORT = None


class Role(Enum):

    MASTER = "master"
    SLAVE = "slave"

    
class InfoHandler:
    role: Role
    host: str
    port: int
    master_host: str
    master_port: int
    def __init__(self, role: Role, host, port, master_host, master_port):
        self.role = role
        self.host = host
        self.port = port
        if role == Role.SLAVE:
            self.master_host = master_host
            self.master_port = master_port
            

    def respond(self):
        response = f"role:{self.role.value}"
        response_len = len(response)
        return f"${response_len}\r\n{response}\r\n"

def getresponce(message):
    if len(message) == 0:
        return "$-1"+ CRFL
    else:
        echoPattern = "$<len>\r\n<data>\r\n"
        echoPattern = echoPattern.replace("<len>", str(len(message)))
        echoPattern = echoPattern.replace("<data>", message)
        return echoPattern


def handle_connection_res(con , addr,info):
    CRLF = "\r\n"
    print("Connected by ",addr)
    with con:        
        while True:
            global myDict
            global flag
            chunk = con.recv(1024)
            if not chunk:
                break
            else:
                vector = chunk.decode().split(CRLF)
                vector2 = []
                for x, i in enumerate(vector):
                    if (x % 2 == 0) & (x != 0):
                        vector2.append(i)
                command = vector2[0].lower()

                if command == "ping":
                    response = getresponce("PONG")
                elif command == "echo":
                    response = getresponce(vector2[1] if len(vector2)>1 else "")
                elif command == "set": 
                    myDict = {vector2[1]: vector2[2]}
                    if len(vector2) > 4:
                        myDict["expiry"] = vector2[-1]
                        myDict["start"] = time.time_ns()
                        flag = True
                    response = getresponce("OK")
                elif command == "get":
                    response = getresponce(myDict[vector2[1]])
                    if(flag):
                        if (time.time_ns() - myDict["start"])* 10**-6 >= int(myDict["expiry"]):
                            response = getresponce("")
                elif command == "info":
                     response = f"$11\r\nrole:{info.role.value}\r\n"

                con.send(response.encode())

                

def main():
    global MASTER_HOST
    global MASTER_PORT
    print("Logs from your program will appear here!")
    host = "localhost"

    parser = argparse.ArgumentParser("Redis server")
    parser.add_argument("--port", type=int, default=6379, help="Port to listen on")
    
  
    args_iter = iter(sys.argv[1:])
    port = DEFAULT_PORT
    for arg in args_iter:
        if arg == "--port":
            port = int(next(args_iter))
        if arg == "--replicaof":
            MASTER_HOST = str(next(args_iter))
            MASTER_PORT = int(next(args_iter))
    
    role = Role.SLAVE if MASTER_PORT is not None else Role.MASTER
    info = InfoHandler(role=role,host=host,port=port,master_host=MASTER_HOST,master_port=MASTER_PORT)
    print("port value is ",port)

    print(MASTER_PORT)
    server_socket = socket.create_server(("localhost", port), reuse_port=True)
    print("server is running on port ",port)
    while True:
        conn , addr = server_socket.accept()
        print('Got connection from',addr)
        thread = threading.Thread(target=handle_connection_res, args=(conn, addr,info))
        thread.start()    
    # wait for client 
if __name__ == "__main__":
    main()
