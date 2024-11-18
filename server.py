import socket
import threading
import argparse

def handle_client(client_socket, address):
    print(f"Connection from {address}")
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"Received from {address}: {data}")
            client_socket.send("Message received".encode('utf-8'))
    except ConnectionResetError:
        print(f"Client {address} disconnected unexpectedly")
    finally:
        client_socket.close()
        print(f"Connection from {address} closed")

def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow socket reuse
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server is listening on {host}:{port}")
    
    try:
        while True:
            client_socket, address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.daemon = True  # Ensures the thread exits when the main program does
            client_thread.start()
    except KeyboardInterrupt:
        print("\nGracefully shutting down the server.")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Traffic Generator Server")
    parser.add_argument("-p", "--port", type=int, default=12345, help="Port to listen on")
    args = parser.parse_args()
    start_server(port=args.port)