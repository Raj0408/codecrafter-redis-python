# Uncomment this to pass the first stage
import socket
import threading
import time
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
    # Assign the role to the server
    MASTER = "master"
    SLAVE = "slave"
   
class InfoHandler:
    # This class will handle the information of the server and client
    role: Role
    host: str
    port: int
    master_host: str
    master_port: int
    master_replid: str
    master_repl_offset:int

    def __init__(self, role: Role, host, port, master_host, master_port):
        self.role = role
        self.host = host
        self.port = port
        if role == Role.SLAVE:
            self.master_host = master_host
            self.master_port = master_port
        self.master_replid = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
        self.master_repl_offset = 0  
            

    def respond(self):
        response = f"role:{self.role.value}"
        response_len = len(response)
        return f"${response_len}\r\n{response}\r\n"

def getresponce(message):
    # This function will return the response to the client
    if len(message) == 0:
        return "$-1"+ CRFL
    else:
        echoPattern = "$<len>\r\n<data>\r\n"
        echoPattern = echoPattern.replace("<len>", str(len(message)))
        echoPattern = echoPattern.replace("<data>", message)
        return echoPattern


def command_checker(vector2,info):
    global myDict
    global flag
    # This function will check the command
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
        # if info.role == Role.MASTER:
        #     response = f"$11\r\nrole:{info.role.value}\r\n"
        #     response += f"$54\r\nmaster_replid:{info.master_replid}\r\n"
        #     response += f"$20\r\nmaster_repl_offset:{info.master_repl_offset}\r\n"
        # else:
        #     response = f"$10\r\nrole:{info.role.value}\r\n"
        #     print("sending re")
        
        response2 = "\n".join(
            [
                f"role:{info.role.value}",
                f"master_replid:{info.role.master_replid}",
                f"master_repl_offset:{info.role.master_repl_offset}",
            ]
        )
        response_len = len(response)
        response = f"${response_len}\r\n{response2}\r\n"

        
    return response.encode()

def handle_connection_res(con , addr,info):
    # This function will handle the connection of the client with the server
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
                print(chunk.decode())
                vector = chunk.decode().split(CRLF)
                vector2 = []
                for x, i in enumerate(vector):
                    if (x % 2 == 0) & (x != 0):
                        vector2.append(i)
                if vector2 is None or len(vector2) == 0:
                    continue
                con.send(command_checker(vector2,info))

                

def main():
    # This is the main function of the server
    global MASTER_HOST
    global MASTER_PORT
    print("Logs from your program will appear here!")
    host = "localhost"

    # parse the command line arguments for host and port number
    args_iter = iter(sys.argv[1:])
    port = DEFAULT_PORT
    for arg in args_iter:
        if arg == "--port":
            port = int(next(args_iter))
        if arg == "--replicaof":
            MASTER_HOST = str(next(args_iter))
            MASTER_PORT = int(next(args_iter))
    
    role = Role.SLAVE if MASTER_PORT is not None else Role.MASTER
    # create the info object
    info = InfoHandler(role=role,host=host,port=port,master_host=MASTER_HOST,master_port=MASTER_PORT)
    print("port value is ",port)

    print(MASTER_PORT)
    # create the server socket
    server_socket = socket.create_server(("localhost", port))
    print("server is running on port ",port)
    while True:
        conn , addr = server_socket.accept()
        print('Got connection from',addr)
        # create a new thread to handle the connection
        thread = threading.Thread(target=handle_connection_res, args=(conn, addr,info))
        thread.start()    
    # wait for client 
if __name__ == "__main__":
    main()
