import socket
import json

def connect_to_server(host='localhost', port=8888):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def send_login(socket_conn, username, password):
    message = {
        "type": "login",
        "username":f"{username}",
        "password":f"{password}"
    }
    print(f"[DEBUG] Sending: {message}")
    socket_conn.sendall(json.dumps(message).encode())
    # socket_conn.sendall(f"LOGIN:{username}:{password}".encode())
    response = socket_conn.recv(1024).decode()
    print(f"[DEBUG] Received from server: {response}")
    return response

def send_register(socket_conn, username, password):
    # message = f"REGISTER:{username}:{password}"
    message = {
        "type": "signup",
        "username":f"{username}",
        "password":f"{password}"
    }
    print(f"[DEBUG] Sending: {message}")

    socket_conn.sendall(json.dumps(message).encode())
    response = socket_conn.recv(1024).decode()
    print(f"[DEBUG] Received from server: {response}")
    return response
