import tkinter as tk
from tkinter import ttk
import threading
import time

class ServerGUI:
    def __init__(self, root, connection_log, transaction_log):
        self.root = root
        self.root.title("Bank Server Monitor")
        self.root.geometry("800x500")

        self.connection_log = connection_log
        self.transaction_log = transaction_log

        self.create_tabs()
        self.update_tables()

    def create_tabs(self):
        tab_control = ttk.Notebook(self.root)

        # Tab 1: Connections / Login / Register
        self.tab_conn = ttk.Frame(tab_control)
        tab_control.add(self.tab_conn, text='Connections & Auth')

        self.conn_tree = ttk.Treeview(self.tab_conn, columns=('Username', 'Action', 'IP', 'Time'), show='headings')
        for col in self.conn_tree["columns"]:
            self.conn_tree.heading(col, text=col)
        self.conn_tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab 2: Transactions
        self.tab_tx = ttk.Frame(tab_control)
        tab_control.add(self.tab_tx, text='Transactions')

        self.tx_tree = ttk.Treeview(self.tab_tx, columns=('Username', 'Action', 'Amount', 'Time'), show='headings')
        for col in self.tx_tree["columns"]:
            self.tx_tree.heading(col, text=col)
        self.tx_tree.pack(expand=True, fill='both', padx=10, pady=10)

        tab_control.pack(expand=True, fill='both')

    def update_tables(self):
        # Update connection log
        for row in self.conn_tree.get_children():
            self.conn_tree.delete(row)
        for entry in self.connection_log:
            self.conn_tree.insert('', 'end', values=entry)

        # Update transaction log
        for row in self.tx_tree.get_children():
            self.tx_tree.delete(row)
        for entry in self.transaction_log:
            self.tx_tree.insert('', 'end', values=entry)

        self.root.after(1000, self.update_tables)  # Update every second
