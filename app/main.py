# Uncomment this to pass the first stage
import socket
import threading
import time

myTime = time.time_ns()
myDict = {}
flag = False


def handle_command(data):
    if(data.startswith("echo")):
        return data[4:]
    else:
        return data


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
                print(vector)
                vector2 = []
                for x, i in enumerate(vector):
                    if (x % 2 == 0) & (x != 0):
                        vector2.append(i)
                print(vector2)

                if vector2[0].lower() == "ping":
                    response = "+PONG{}".format(CRLF)
                elif vector2[0].lower() == "echo":
                    response = "+" + vector2[1] + CRLF
                elif vector2[0].lower() == "set": 
                    myDict = {vector2[1]: vector2[2]}
                    if len(vector2) > 4:
                        myDict["expiry"] = vector2[-1]
                        myDict["start"] = time.time_ns()
                        flag = True
                    response = "+OK" + CRLF
                elif vector2[0] == "get":
                    if(flag):
                        if (time.time_ns() - myDict["start"]) > int(myDict["expiry"]):
                            response = "-1" + CRLF
                        else:
                            response = "+" + myDict[vector2[1]] + CRLF
                con.send(response.encode())

                

def main():
    
    print("Logs from your program will appear here!")
    my_time = time.time_ns() * 10 ** -6
    print(my_time)
    
    server_socket = socket.create_server(("localhost", 6379))
    server_socket.listen()
    while True:
        conn , addr = server_socket.accept()
        thread = threading.Thread(target=handle_connection_res, args=(conn, addr))
        thread.start()    
    # wait for client 
if __name__ == "__main__":
    main()
