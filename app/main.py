# Uncomment this to pass the first stage
import socket
import threading
import time
from enum import Enum
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

class RaplicaHandler:
    sock = None

    def __init__(self ,info):
        self.info = info
        if info.role == Role.SLAVE:
            self.sock = socket.create_connection(
                (info.master_host, info.master_port)
            )

    def start_slave(self):
        self._ping()
        self._replconf()
        self._psync()

    def _ping(self):
        ping_command = "*1\r\n" + getresponce("PING")
        sent_bytes = self.sock.send(str.encode(ping_command))
        if sent_bytes == 0:
            print("Failure connecting to Master")
        response = self.sock.recv(1024)

    def _replconf(self):
        replconf_command_port = "*3\r\n" + getresponce("REPLCONF") + getresponce("listening-port") + getresponce("6380")
        sent_bytes = self.sock.send(str.encode(replconf_command_port))
        if sent_bytes == 0:
            print("Failure connecting to Master")
        response = self.sock.recv(1024)
        print(response)
        # `REPLCONF listening-port <port>
        replconf_command_cap = "*3\r\n" + getresponce("REPLCONF") + getresponce("capa") + getresponce("psync2")
        sent_bytes = self.sock.send(str.encode(replconf_command_cap))
        if sent_bytes == 0:
            print("Failure connecting to Master")
        response = self.sock.recv(1024)
        # replcaonf capabilites

    def _psync(self):
        psync_command = "*3\r\n" + getresponce("PSYNC") + getresponce("?") + getresponce("-1")
        sent_bytes = self.sock.send(str.encode(psync_command))
        if sent_bytes == 0:
            print("Failure connecting to Master")
        response = self.sock.recv(1024)
        print(response)


class Redis:

    server_socket = None

    def __init__(self,info) -> None:

        if(info.role == Role.SLAVE):
            Raplica = RaplicaHandler(info)
            Raplica.start_slave()
        
        host = info.host
        port = info.port
        server_socket = socket.create_server((host, port))
        print("server is running on port ",port)
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_connection_res, args=(conn, addr,info)
            )
            client_thread.start()
        




        # self.info = info
        # self.server_socket = socket.create_server(("localhost", info.port))
        # print("server is running on port ",info.port)
        # Raplica = RaplicaHandler(info)
        # Raplica.start_slave()
        

    # def server_up(self,socket,info):
       

        
    
        

def getresponce(message):
    # This function will return the response to the client
    if len(message) == 0:
        return "$-1"+ CRFL
    else:
        echoPattern = "$<len>\r\n<data>\r\n"
        echoPattern = echoPattern.replace("<len>", str(len(message)))
        echoPattern = echoPattern.replace("<data>", message)
        return echoPattern

def master_ping(info):
    sc = socket.socket()
    sc.connect((info.master_host, info.master_port))



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
        print("this is the info section ")
        response = f"role:{info.role.value}\r\n"
        response += f"master_replid:{info.master_replid}\r\n"
        response += f"master_repl_offset:{info.master_repl_offset}\r\n"
        response = getresponce(response)

    elif command == "replconf" or vector2[1] == "listening-port":
        response = getresponce("OK")
    elif command == "replconf" or vector2[1] == "capa":
        response = getresponce("OK")
    elif command == "psync":
        response = f"+FULLRESYNC {info.master_replid} {0}\r\n"
        response = getresponce(response)
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
    m_conn = None
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
    redis = Redis(info)
    redis.server_up()
    # create the server socket   
    # wait for client 
if __name__ == "__main__":
    main()
