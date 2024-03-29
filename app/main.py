# Uncomment this to pass the first stage
import socket
import threading
import time
from enum import Enum
import sys
import base64

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

def getresponce(message,trailing = True):
    # This function will return the response to the client
    if len(message) == 0:
        return "$-1"+ CRFL
    else:
        echoPattern = "$<len>\r\n<data>"
        echoPattern = echoPattern.replace("<len>", str(len(message)))
        echoPattern = echoPattern.replace("<data>", message)

        if trailing:
            return echoPattern+"\r\n"
        else:
            return echoPattern

def master_ping(info):
    sc = socket.socket()
    sc.connect((info.master_host, info.master_port))

def ping(vecntor2 ,info,con):
    # This function will handle the ping command
    response = getresponce("PONG")
    con.send(response.encode())
def echo(vector2,info,con):
    # This function will handle the echo command
    response = getresponce(vector2[1] if len(vector2)>1 else "")
    con.send(response.encode())
def set(vector2,info,con):
    # This function will handle the set command
    global myDict
    global flag
    myDict = {vector2[1]: vector2[2]}
    if len(vector2) > 4:
        myDict["expiry"] = vector2[-1]
        myDict["start"] = time.time_ns()
        flag = True
    response = getresponce("OK")
    con.send(response.encode())

def get(vector2,info,con):
    # This function will handle the get command

    global myDict
    global flag
    response = getresponce(myDict[vector2[1]])
    if(flag):
        if (time.time_ns() - myDict["start"])* 10**-6 >= int(myDict["expiry"]):
            response = getresponce("")
    con.send(response.encode())
def info(vector2,info,con):
    # This function will handle the info command
    print("this is the info section ")
    response = f"role:{info.role.value}\r\n"
    response += f"master_replid:{info.master_replid}\r\n"
    response += f"master_repl_offset:{info.master_repl_offset}\r\n"
    con.send(getresponce(response).encode())

def replconf(vector2 ,info,con):
    # This function will handle the replconf command
    response = getresponce("OK")
    con.send(response.encode())

def psync(vector2,info,con):
    # This function will handle the psync command
    response = f"+FULLRESYNC {info.master_replid} {0}\r\n"
    # con.send(response.encode())
    empy_file = "UkVESVMwMDEx+glyZWRpcy12ZXIFNy4yLjD6CnJlZGlzLWJpdHPAQPoFY3RpbWXCbQi8ZfoIdXNlZC1tZW3CsMQQAPoIYW9mLWJhc2XAAP/wbjv+wP9aog=="
    binary_file = base64.b64decode(empy_file)
    response += getresponce(binary_file)
    print(response)
    con.send(getresponce(response).encode())


f_trigger = {
    "ping": ping,
    "echo": echo,
    "set": set,
    "get": get,
    "info": info,
    "replconf": replconf,
    "psync": psync
}

def command_checker(vector2,info,con):
    global myDict
    global flag
    # This function will check the command
    command = vector2[0].lower()

    if command in f_trigger:
        f_trigger[command](vector2,info,con)

def handle_connection_res(con , addr,info):
    # This function will handle the connection of the client with the server
    CRLF = "\r\n"
    print("Connected by ",addr)
    checker = False
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
                command_checker(vector2,info,con)
                if checker:
                    con.send(getresponce())

                

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
    Redis(info)
    # create the server socket   
    # wait for client 
if __name__ == "__main__":
    main()
