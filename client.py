import socket
import time
import argparse
from datetime import datetime
import mysql.connector
from mysql.connector import errorcode

# Obtain connection string information from the portal
config = {
  'host':'server-client-logs.mysql.database.azure.com',
  'user':'admin498',
  'password':'m!ntch0c0l@te',
  'database':'server-client-logs'
}

# Construct connection string
try:
   conn = mysql.connector.connect(**config)
   print("Connection established")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with the user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cursor = conn.cursor()

def start_client(server_address, server_port, msg_interval, log_file, client_region, server_region):
    # Get the current date in YYYY_MM_DD
    current_date = datetime.now().strftime('%Y_%m_%d')

    # Construct the table name
    table_name = f"connection_logs_{current_date}"

    # Create table query with table name
    create_table_query = f"""
    CREATE TABLE {table_name} (
        start_time DATETIME PRIMARY KEY, 
        end_time DATETIME, 
        client_region VARCHAR(100), 
        server_region VARCHAR(100), 
        latency INTEGER
    );
    """

    # Execute the query, creates the table
    cursor.execute(create_table_query)

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

                        # Insert the record into the database
                        insert_query = f"""
                        INSERT INTO {table_name} (start_time, end_time, client_region, server_region, latency)
                        VALUES (%s, %s, %s, %s, %s);
                        """
                        cursor.execute(insert_query, (start_time, end_time, client_region, server_region, latency))
                        conn.commit()
                        
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
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Generate default log file with current date and time
    default_logfile = f"latency_log_{datetime.now().strftime('%m-%d-%Y_%H:%M:%S')}.txt"
    
    parser = argparse.ArgumentParser(description="TCP Traffic Generator Client")
    parser.add_argument("-a", "--address", type=str, required=True, help="Server IP address")
    parser.add_argument("-p", "--port", type=int, required=True, default=12345, help="Server port number")
    parser.add_argument("-i", "--interval", type=int, default=5, help="Interval (in seconds) between each message")
    parser.add_argument("-l", "--logfile", type=str, default=default_logfile, help="File to log latency values")
    args = parser.parse_args()
    
    start_client(args.address, args.port, args.interval, args.logfile, \
                 args.client_region, args.server_region)