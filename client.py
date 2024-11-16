import socket
import time
import argparse

def start_client(server_address, server_port, msg_interval):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Attempting to connect to {server_address}:{server_port}")
            client_socket.connect((server_address, server_port))
            print("Connected to server!")
            
            while True:
                try:
                    start_time = time.time()
                    client_socket.send("Hello, Server!".encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000  # milliseconds
                    print("Received from server:", response)
                    print(f"Round-trip latency: {latency:.2f} ms")
                    time.sleep(msg_interval)
                except (BrokenPipeError, ConnectionResetError):
                    print("Connection lost. Attempting to reconnect...")
                    client_socket.close()
                    raise  # This will trigger the outer try/except
                
        except (ConnectionRefusedError, BrokenPipeError, ConnectionResetError) as e:
            print(f"Connection error: {e}")
            print("Waiting 5 seconds before retry...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nClient stopped. Graceful disconnect.")
            break
        finally:
            client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Traffic Generator Client")
    parser.add_argument("-a", "--address", type=str, required=True, help="Server IP address")
    parser.add_argument("-p", "--port", type=int, default=12345, help="Server port number")
    parser.add_argument("-i", "--interval", type=int, default=5, help="Interval (in seconds) between each message")
    args = parser.parse_args()
    
    start_client(args.address, args.port, args.interval)