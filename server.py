import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
    server_socket.bind(('localhost', 12345)) #IP, Port
    server_socket.listen(3)  # Listening up to 3 connections - can adjust later
    print("Server is listening on port 12345")

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address}")
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print("Received from client:", data)
                client_socket.send("Message received".encode('utf-8'))
            client_socket.close()
    except KeyboardInterrupt:
        print("\nGracefully shutting down the server.")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    start_server()