import client.client_socket as client_socket
from client.session_state import SessionState
import tkinter as tk
from tkinter import messagebox

class ATMClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure ATM Client")
        self.root.geometry("400x300")

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.amount = tk.StringVar()

        self.session = SessionState()
        self.create_login_frame()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_login_frame(self):
        self.clear_root()
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=40)

        # Title (optional)
        tk.Label(self.login_frame, text="Welcome to Secure ATM", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Username
        tk.Label(self.login_frame, text="Username:", font=("Helvetica", 12)).grid(row=1, column=0, pady=5, padx=10, sticky="e")
        tk.Entry(self.login_frame, textvariable=self.username, font=("Helvetica", 12), width=20).grid(row=1, column=1, pady=5)

        # Password
        tk.Label(self.login_frame, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, pady=5, padx=10, sticky="e")
        tk.Entry(self.login_frame, textvariable=self.password, font=("Helvetica", 12), show="*", width=20).grid(row=2, column=1, pady=5)

        # Button frame
        button_frame = tk.Frame(self.login_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Login", width=12, font=("Helvetica", 11), command=self.handle_login).pack(side="left", padx=10)
        tk.Button(button_frame, text="Register", width=12, font=("Helvetica", 11), command=self.handle_register).pack(side="left", padx=10)


    def handle_login(self):
        user = self.username.get()
        pwd = self.password.get()

        if user and pwd:
            try:
                sock = client_socket.connect_to_server()
                result = client_socket.send_login(sock, user, pwd)

                if result == "SUCCESS":
                    self.session.username = user
                    self.session.socket = sock
                    self.create_main_menu_frame()
                else:
                    messagebox.showerror("Login Failed", "Invalid credentials.")
            except Exception as e:
                messagebox.showerror("Error", f"Connection failed: {e}")
        else:
            messagebox.showerror("Error", "Please enter both username and password.")
    

    def handle_register(self):
        user = self.username.get()
        pwd = self.password.get()

        print("[DEBUG] Register clicked")
        print(f"[DEBUG] Username: {user} | Password: {pwd}")

        if user and pwd:
            try:
                sock = client_socket.connect_to_server()
                print("[DEBUG] Connected to server")

                result = client_socket.send_register(sock, user, pwd)
                print(f"[DEBUG] Server response: {result}")

                if result == "SUCCESS":
                    messagebox.showinfo("Registered", "Account created! You can now log in.")
                else:
                    messagebox.showerror("Error", "Username already exists.")
                sock.close()
            except Exception as e:
                messagebox.showerror("Error", f"Connection failed: {e}")
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    def create_main_menu_frame(self):
        self.clear_root()
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=30)

        tk.Label(self.menu_frame, text="Amount").grid(row=0, column=0, pady=5)
        tk.Entry(self.menu_frame, textvariable=self.amount).grid(row=0, column=1, pady=5)

        tk.Button(self.menu_frame, text="Deposit", command=self.deposit).grid(row=1, column=0, pady=5)
        tk.Button(self.menu_frame, text="Withdraw", command=self.withdraw).grid(row=1, column=1, pady=5)
        tk.Button(self.menu_frame, text="Balance Inquiry", command=self.balance_inquiry).grid(row=2, columnspan=2, pady=5)

        self.message_label = tk.Label(self.menu_frame, text="", fg="blue")
        self.message_label.grid(row=3, columnspan=2, pady=10)

    def deposit(self):
        self.show_message(f"Deposit requested for ${self.amount.get()}")

    def withdraw(self):
        self.show_message(f"Withdraw requested for ${self.amount.get()}")

    def balance_inquiry(self):
        self.show_message("Balance inquiry requested")

    def show_message(self, msg):
        self.message_label.config(text=msg)


