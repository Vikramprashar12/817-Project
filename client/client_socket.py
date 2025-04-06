import hashlib
import hmac
import os
import secrets
import socket
import json
import traceback
from dotenv import load_dotenv
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from shared.crypto_utils import (
    encrypt_with_AES_key,
    decrypt_with_AES_key,
    generate_master_secret_from_pms,
    generate_enc_and_MAC_key,
    secure_receive,
    secure_send
)

load_dotenv()

def connect_to_server(session, host='localhost', port=8888):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    atm_info = json.loads(s.recv(1024).decode())
    session.atm_number = atm_info["atm_number"]
    print(f"[DEBUG] Connected to ATM #{session.atm_number}")

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

def send_transaction(socket_conn, username, action, amount=0, ENC_KEY=None, MAC_KEY=None):
    if ENC_KEY is None or MAC_KEY is None:
        raise ValueError("Encryption and MAC keys must be provided")

    payload = {
        "type": "transaction",
        "username": username,
        "action": action
    }

    if action in ["deposit", "withdraw"]:
        payload["amount"] = amount

    secure_payload = secure_send(payload, ENC_KEY, MAC_KEY)
    socket_conn.sendall(json.dumps(secure_payload).encode())

    response_raw = socket_conn.recv(2048).decode()
    response_packet = json.loads(response_raw)
    decrypted = secure_receive(response_packet, ENC_KEY, MAC_KEY)
    print("[DEBUG] Server transaction response:", decrypted)

    return decrypted

def perform_secure_register(sock, username, password, session):
    try:
        atm_number = session.atm_number or 1
        shared_secret = os.getenv("ATM_SERVER_SHARED_SECRET")
        salt = os.getenv(f"ATM_{atm_number}_SALT")
        print(f"[DEBUG] ATM_{atm_number}_SALT: {salt}")
        print(f"[DEBUG] ATM_SERVER_SHARED_SECRET: {shared_secret}")
        if not shared_secret or not salt:
            raise Exception("Missing ATM_SERVER_SHARED_SECRET or ATM_<n>_SALT")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=10000,
            backend=default_backend()
        )
        K_s = kdf.derive(shared_secret.encode())

        iv = secrets.token_bytes(16)
        payload = {
            "username": username,
            "password": password,
            "atm_number": atm_number
        }

        encrypted_payload = encrypt_with_AES_key(json.dumps(payload), K_s, iv)

        register_msg = {
            "type": "auth",
            "step": 0,
            "atm_number": atm_number,
            "iv": iv.hex(),
            "encr_payload": encrypted_payload.hex()
        }

        sock.sendall(json.dumps(register_msg).encode())

        response = json.loads(sock.recv(2048).decode())
        return response
    except Exception as e:
        print(f"[ERROR] Secure register failed: {e}")
        traceback.print_exc()
        return False

def perform_secure_login(sock, username, password, session):
    try:
        # === 1. Generate pre-shared key K_s ===
        atm_number = session.atm_number or 1
        shared_secret = os.getenv("ATM_SERVER_SHARED_SECRET")
        salt = os.getenv(f"ATM_{atm_number}_SALT")
        print(f"[DEBUG] ATM_{atm_number}_SALT: {salt}")
        print(f"[DEBUG] ATM_SERVER_SHARED_SECRET: {shared_secret}")
        if not shared_secret or not salt:
            raise Exception("Missing ATM_SERVER_SHARED_SECRET or ATM_<n>_SALT in .env")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=10000,
            backend=default_backend()
        )
        K_s = kdf.derive(shared_secret.encode())

        # === 2. Generate nonce and send encrypted credentials + nonce ===
        N_atm = secrets.randbelow(10_000_000)
        payload = {
            "type": "login",
            "username": username,
            "password": password,
            "N_atm": N_atm
        }

        iv1 = secrets.token_bytes(16)
        encrypted_payload = encrypt_with_AES_key(json.dumps(payload), K_s, iv1)
        msg1 = {
            "type": "auth",
            "step": 1,
            "atm_number": atm_number,
            "iv": iv1.hex(),
            "encr_payload": encrypted_payload.hex()
        }
        sock.sendall(json.dumps(msg1).encode())

        # === 3. Receive challenge response with N_s and echoed N_atm ===
        msg2 = json.loads(sock.recv(2048).decode())
        print(f"[DEBUG] Raw step 2 response: '{msg2}'")
        iv2 = bytes.fromhex(msg2["iv"])
        ciphertext2 = bytes.fromhex(msg2["encr_payload"])
        response = json.loads(decrypt_with_AES_key(ciphertext2, K_s, iv2))

        if response["N_atm"] != N_atm:
            raise Exception("N_atm mismatch — authentication failed.")
        N_s = response["N_s"]

        # === 4. Send back N_s confirmation ===
        iv3 = secrets.token_bytes(16)
        encrypted_Ns = encrypt_with_AES_key(json.dumps({"N_s": N_s}), K_s, iv3)
        msg3 = {
            "type": "auth",
            "step": 3,
            "iv": iv3.hex(),
            "payload": encrypted_Ns.hex()
        }
        sock.sendall(json.dumps(msg3).encode())

        # === 5. Wait for success confirmation ===
        raw_response = sock.recv(2048).decode()
        print(f"[DEBUG] Raw step 4 response: '{raw_response}'")
        msg4 = json.loads(raw_response)

        if msg4.get("status") != "success":
            raise Exception("Authentication rejected by server.")

        # === 6. Send pre-master secret (PMS) ===
        PMS = "vikram_likes_meta_LLMs"
        iv5 = secrets.token_bytes(16)
        encrypted_pms = encrypt_with_AES_key(json.dumps({"pms": PMS, "username": username, "password": password}), K_s, iv5)
        msg5 = {
            "type": "auth",
            "step": 5,
            "iv": iv5.hex(),
            "payload": encrypted_pms.hex()
        }
        sock.sendall(json.dumps(msg5).encode())

        # === 7. Wait for final auth confirmation from server ===
        raw_response = sock.recv(2048).decode()
        print(f"[DEBUG] Raw step 5 response: '{raw_response}'")
        try:
            final_response = json.loads(raw_response)
            print(f"[DEBUG] Final auth response: {final_response}")
        except json.JSONDecodeError:
            sock.close()
            raise Exception("Invalid server response.")


        if final_response.get("type") != "auth" or final_response.get("status") != "success":
            sock.close()
            raise Exception(final_response.get("message", "Authentication failed."))


        # === 7. Derive session keys ===
        master_secret = generate_master_secret_from_pms(PMS, atm_number, N_atm, N_s)
        ENC_KEY, MAC_KEY = generate_enc_and_MAC_key(master_secret, PMS.encode())

        # === 8. Save into session ===
        session.username = username
        session.socket = sock
        session.encryption_key = ENC_KEY
        session.mac_key = MAC_KEY

        return True
    except Exception as e:
        print(f"[ERROR] Secure login failed: {e}")
        traceback.print_exc()
        return False