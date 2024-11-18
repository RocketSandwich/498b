import socket
import time
import argparse
from datetime import datetime

def start_client(server_address, server_port, msg_interval, log_file):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Attempting to connect to {server_address}:{server_port}")
            client_socket.connect((server_address, server_port))
            print("Connected to server!")
            
            # Get client's local IP and port after connection
            client_ip, client_port = client_socket.getsockname()
            
            # Open the log file in append mode and write header if empty
            with open(log_file, 'a') as file:
                # Write the header line at the start of the file
                file.seek(0, 2)
                if file.tell() == 0:  # Check if the file is empty
                    file.write(f"{client_ip}:{client_port} <-> {server_address}:{server_port}\n")
                
                while True:
                    try:
                        start_time = time.time()
                        client_socket.send("Hello, Server!".encode('utf-8'))
                        response = client_socket.recv(1024).decode('utf-8')
                        end_time = time.time()
                        latency = (end_time - start_time) * 1000  # milliseconds
                        
                        # Print and log latency
                        print("Received from server:", response)
                        print(f"Round-trip latency: {latency:.2f} ms")
                        file.write(f"{latency:.2f}\n")
                        file.flush()  # Ensure the data is written to the file immediately
                        
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
    # Generate default log file with current date and time
    default_logfile = f"latency_log_{datetime.now().strftime('%m-%d-%Y_%H:%M:%S')}.txt"
    
    parser = argparse.ArgumentParser(description="TCP Traffic Generator Client")
    parser.add_argument("-a", "--address", type=str, required=True, help="Server IP address")
    parser.add_argument("-p", "--port", type=int, required=True, default=12345, help="Server port number")
    parser.add_argument("-i", "--interval", type=int, default=5, help="Interval (in seconds) between each message")
    parser.add_argument("-l", "--logfile", type=str, default=default_logfile, help="File to log latency values")
    args = parser.parse_args()
    
    start_client(args.address, args.port, args.interval, args.logfile)