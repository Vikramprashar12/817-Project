
class SessionState:
    def __init__(self):
        self.username = None
        self.master_secret = None
        self.encryption_key = None
        self.mac_key = None
        self.socket = None  # Store the socket connection to the server
        self.atm_number = None  # Store the ATM number for the session
