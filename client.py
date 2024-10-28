import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

# Send data to server
client_socket.send("Hello, Server!".encode('utf-8'))

# Receive server response
response = client_socket.recv(1024).decode('utf-8')
print("Received from server:", response)

client_socket.close()