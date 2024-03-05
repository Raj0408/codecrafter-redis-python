# Uncomment this to pass the first stage
import socket
import threading


def handle_command(data):
    if(data.startswith("echo")):
        return data[4:]
    else:
        return data


def handle_connection_res(con , addr):
    CRLF = "\r\n"
    print("Connected by ",addr)
    with con:
        data = ""
        while True:
            chunk = con.recv(1024)
            if not chunk:
                break
            else:
                vector = chunk.decode().split(CRLF)
                print(vector)
                if vector[2].lower() == "ping":
                    response = "+PONG{}".format(CRLF)
                elif vector[2].lower() == "echo":
                    response = "+" + vector[4] + CRLF
                elif vector[2].lower() == "set":
                    myDict = {vector[4]: vector[6]}
                    response = "+OK" + CRLF
                elif vector[2] == "get":
                    response = "+" + myDict[vector[4]] + CRLF
                con.send(response.encode())

                

def main():
    
    print("Logs from your program will appear here!")
    
    server_socket = socket.create_server(("localhost", 6379))
    server_socket.listen()
    while True:
        conn , addr = server_socket.accept()
        thread = threading.Thread(target=handle_connection_res, args=(conn, addr))
        thread.start()    
    # wait for client 
if __name__ == "__main__":
    main()
