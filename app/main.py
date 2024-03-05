# Uncomment this to pass the first stage
import socket
import threading


def handle_connection_res(con , addr):
    ping = "+PONG\r\n"
    print("Connected by ",addr)
    with con:
        while True:
            data = con.recv(1024)
            if not data:
                break
            else:
                print(f"Received from {con}: ",data.decode())
                con.send(ping.encode())

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
