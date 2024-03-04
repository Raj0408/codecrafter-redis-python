# Uncomment this to pass the first stage
import socket


def main():
    
    print("Logs from your program will appear here!")
    ping = "PING\r\n"
    server_socket = socket.create_server(("localhost", 6379))
    con , addr = server_socket.accept() # wait for client
    print("Connected by ",addr)
    with con:
        con.recv(1024)
        con.send(ping.encode())

if __name__ == "__main__":
    main()
