import socket

def connect_to_server(host='localhost', port=8888):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def send_login(socket_conn, username, password):
    socket_conn.sendall(f"LOGIN:{username}:{password}".encode())
    response = socket_conn.recv(1024).decode()
    return response

def send_register(socket_conn, username, password):
    message = f"REGISTER:{username}:{password}"
    print(f"[DEBUG] Sending: {message}")
    socket_conn.sendall(message.encode())
    response = socket_conn.recv(1024).decode()
    print(f"[DEBUG] Received from server: {response}")
    return response
