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
  # Get the current date and time in YYYY_MM_DD_HH_MM_SS
  current_date = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

  # Construct the table name
  table_name = f"connection_logs_{current_date}"

  # Create table query with table name
  create_table_query = f"""
  CREATE TABLE {table_name} (
      index_id INT AUTO_INCREMENT PRIMARY KEY, 
      start_time FLOAT, 
      end_time FLOAT, 
      client_region VARCHAR(100), 
      server_region VARCHAR(100), 
      latency INTEGER,
      jitter FLOAT,
      packet_loss INTEGER,
      throughput FLOAT
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
          
        previous_latency = None
        packet_loss = 0  # Initialize packet loss counter
        
        while True:
          try:
            start_time = time.time()
            message = "a" * 1000  # 1000 bytes
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            end_time = time.time()

            # Latency in milliseconds
            latency = (end_time - start_time) * 1000  # milliseconds

            # Jitter (difference between consecutive latencies)
            jitter = abs(latency - previous_latency) if previous_latency is not None else 0
            previous_latency = latency

            # Throughput (bytes per millisecond)
            throughput = len(message) / latency if latency > 0 else 0
            
            # Log metrics to file and print to console
            print(f"Received from server: {response}")
            print(f"Latency: {latency:.2f} ms, Jitter: {jitter:.2f} ms, Throughput: {throughput:.2f} B/ms")
            file.write(f"{latency:.2f},{jitter:.2f},{throughput:.2f}\n")
            file.flush()

            # Insert metrics into database
            insert_query = f"""
            INSERT INTO {table_name} (start_time, end_time, client_region, server_region, latency, jitter, packet_loss, throughput)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (start_time, end_time, client_region, server_region, latency, jitter, packet_loss, throughput))
            conn.commit()

            
            time.sleep(msg_interval)
          except (BrokenPipeError, ConnectionResetError):
            print("Connection lost. Attempting to reconnect...")
            client_socket.close()
            raise  # This will trigger the outer try/except
            
    except (ConnectionRefusedError, BrokenPipeError, ConnectionResetError) as e:
      packet_loss += 1  # Increment packet loss counter
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
  parser.add_argument("-cr", "--clientregion", type=str, required=True, help="Client region")
  parser.add_argument("-sr", "--serverregion", type=str, required=True, help="Server region")
  args = parser.parse_args() 
  
  start_client(args.address, args.port, args.interval, args.logfile, \
                args.clientregion, args.serverregion)