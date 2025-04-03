import json
import socket
import threading
import os
from gui_server import ServerGUI
import tkinter as tk
from logger import log_connection_event, log_transaction_event


USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    print("[DEBUG] Saving users to file...")
    with open(USER_FILE, "w") as f:
        json.dump(users, f)
    print("[DEBUG] Save complete.")


USER_DATABASE = load_users()

HOST = 'localhost'
PORT = 8888

def handle_client(conn, addr, connection_log, transaction_log):
    print(f"[+] Connection from {addr}")

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            if data.startswith("LOGIN:"):
                _, username, password = data.split(":", 2)
                username = username.strip()
                password = password.strip()
                print(f"[>] Login attempt: {username}")

                if USER_DATABASE.get(username) == password:
                    conn.sendall("SUCCESS".encode())
                    log_connection_event(connection_log, username, "login", addr[1])
                else:
                    conn.sendall("FAIL".encode())
            elif data.startswith("REGISTER:"):
                _, username, password = data.split(":", 2)
                username = username.strip()
                password = password.strip()
                print(f"[>] Register attempt: {username}")
                if username in USER_DATABASE:
                    conn.sendall("FAIL".encode())
                else:
                    USER_DATABASE[username] = password
                    save_users(USER_DATABASE)
                    conn.sendall("SUCCESS".encode())
                    log_connection_event(connection_log, username, "register", addr[1])
            else:
                conn.sendall("UNKNOWN_COMMAND".encode())
    except Exception as e:
        print(f"[!] Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Disconnected: {addr}")

if __name__ == "__main__":
    connection_log = []
    transaction_log = []

    def start_server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"[+] Server listening on {HOST}:{PORT}")

            while True:
                conn, addr = server_socket.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr, connection_log, transaction_log))
                thread.start()

    # Start server thread
    threading.Thread(target=start_server, daemon=True).start()

    # Start GUI
    root = tk.Tk()
    gui = ServerGUI(root, connection_log, transaction_log)
    root.mainloop()


