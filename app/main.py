# Uncomment this to pass the first stage
import socket
import threading
import time
from app.cliparse import CLIArgParser
from enum import Enum, auto
import sys


myTime = time.time_ns()
myDict = {}
flag = False

DEFAULT_PORT = 6379
CRFL = "\r\n"


class Role(Enum):

    MASTER = "master"
    SLAVE = "slave"

    
class InfoHandler:
    role: Role
    host: str
    port: int
    def __init__(self, role: Role):
        self.role = role
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
                if command == "echo":
                    response = getresponce(vector2[1] if len(vector2)>1 else "")
                if command == "set": 
                    myDict = {vector2[1]: vector2[2]}
                    if len(vector2) > 4:
                        myDict["expiry"] = vector2[-1]
                        myDict["start"] = time.time_ns()
                        flag = True
                    response = getresponce("OK")
                if command == "get":
                    response = getresponce(myDict[vector2[1]])
                    if(flag):
                        if (time.time_ns() - myDict["start"])* 10**-6 >= int(myDict["expiry"]):
                            response = getresponce("")
                if command == "info":
                     response = f"$11\r\nrole:{info.role.name}\r\n"

                con.send(response.encode())

                

def main():
    
    print("Logs from your program will appear here!")
    host = "localhost"
    master_port: int = None
    args = CLIArgParser().parse_args()
    args_iter = iter(sys.argv[1:])
    port = DEFAULT_PORT
    for arg in args_iter:
        if arg == "--port":
            port = int(next(args_iter))
        if arg == "--replicaof":
            host = str(next(args_iter))
            master_port = int(next(args_iter))
    info = InfoHandler(Role.SLAVE if master_port is not None else Role.MASTER)
    info.host = host
    info.port = port

    server_socket = socket.create_server((info.host, info.port))
    server_socket.listen()
    while True:
        conn , addr = server_socket.accept()
        thread = threading.Thread(target=handle_connection_res, args=(conn, addr,info))
        thread.start()    
    # wait for client 
if __name__ == "__main__":
    main()
