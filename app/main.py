# Uncomment this to pass the first stage
import socket
import threading
import time
from app.cliparse import CLIArgParser
from enum import Enum, auto


myTime = time.time_ns()
myDict = {}
flag = False

DEFAULT_PORT = 6379
CRFL = "\r\n"


class Role(Enum):

    MASTER = "master"

    
class InfoHandler:
    role: Role
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


def handle_connection_res(con , addr):
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

                if vector2[0].lower() == "ping":
                    response = getresponce("PONG")
                elif vector2[0].lower() == "echo":
                    response = getresponce(vector2[1] if len(vector2)>1 else "")
                elif vector2[0].lower() == "set": 
                    myDict = {vector2[1]: vector2[2]}
                    if len(vector2) > 4:
                        myDict["expiry"] = vector2[-1]
                        myDict["start"] = time.time_ns()
                        flag = True
                    response = getresponce("OK")
                elif vector2[0] == "get":
                    response = getresponce(myDict[vector2[1]])
                    if(flag):
                        if (time.time_ns() - myDict["start"])* 10**-6 >= int(myDict["expiry"]):
                            response = getresponce("")
                elif vector2[0].lower() == "info":
                    response = InfoHandler(Role.MASTER)
                con.send(response.encode())

                

def main():
    
    print("Logs from your program will appear here!")
    args = CLIArgParser().parse_args()
    try:
        port = int(args.port)
    except:
        port = 6379
    server_socket = socket.create_server(("localhost", port))
 
    # server_socket = socket.create_server(("localhost", port))
    server_socket.listen()
    while True:
        conn , addr = server_socket.accept()
        thread = threading.Thread(target=handle_connection_res, args=(conn, addr))
        thread.start()    
    # wait for client 
if __name__ == "__main__":
    main()
