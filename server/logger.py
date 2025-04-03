from datetime import datetime

def log_connection_event(log_list, username, action, ip):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_list.append((username, action, ip, timestamp))

def log_transaction_event(log_list, username, action, amount=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_list.append((username, action, amount, timestamp))
