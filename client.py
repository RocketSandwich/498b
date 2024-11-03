import socket
import time
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="TCP Traffic Generator for latency measurement")
    parser.add_argument("-a", "--address", type=str, default="localhost", help="Server IP address or hostname")
    parser.add_argument("-p", "--port", type=int, default=12345, help="Server port number")
    parser.add_argument("-i", "--interval", type=int, default=5, help="Interval (in seconds) between each message")
    args = parser.parse_args()

    server_address = args.address
    server_port = args.port
    msg_interval = args.interval

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))

        while True:
            try:
                start_time = time.time()

                client_socket.send("Hello, Server!".encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')

                end_time = time.time()

                latency = (end_time - start_time) * 1000  # milliseconds
                print("Received from server:", response)
                print(f"Round-trip latency: {latency:.2f} ms")

                time.sleep(msg_interval) # default 5 seconds
            except BrokenPipeError:
                print("Connection lost. Attempting to reconnect...")
                time.sleep(5)  # Wait 
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server_address, server_port))

    except KeyboardInterrupt:
        print("Client stopped. Graceful disconnect.")

    finally:
        # Close the socket connection
        client_socket.close()