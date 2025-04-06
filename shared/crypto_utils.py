
import hmac
import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib
import json

NUM_ITERATIONS = 10000

# decrypt data encrypted with shared key (K_s)
def decrypt_with_AES_key(encr_data: bytes, key: bytes, IV: bytes):
    cipher = Cipher(algorithms.AES(key), modes.CBC(IV), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encr_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder() 
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data.decode('utf-8')

# encrypt data with shared key (K_s)
def encrypt_with_AES_key(data: bytes, key: bytes, IV: bytes):
    data_bytes= data.encode('utf-8')
    padder = padding.PKCS7(128).padder()  # AES block size is 128 bits (16 bytes)
    padded_data = padder.update(data_bytes) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()
    encr_data = encryptor.update(padded_data) + encryptor.finalize()
    return encr_data

# ensure a string is 16 bytes 
def pad_string_to_16_bytes(string: str):
    string_bytes = string.encode('utf-8')
    if len(string_bytes) == 16:
        return string_bytes
    elif len(string_bytes) > 16:
        return string_bytes[:16]
    else:
        padder = padding.PKCS7(128).padder()
        return padder.update(string_bytes) + padder.finalize()

# generates master secret from 
def generate_master_secret_from_pms(pre_master_secret: str, atm_number: int, client_nonce: int, server_nonce: int) -> bytes:
    # for now let the salt be from the .env file
    salt_str = str(os.getenv(f"ATM_{atm_number}_SALT"))
    # add the nonces to pre master secret
    pre_master_secret += f"{client_nonce}{server_nonce}"
    pre_master_secret_bytes = pre_master_secret.encode('utf-8')
    salt_bytes = pad_string_to_16_bytes(salt_str)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  
        salt=salt_bytes,
        iterations=NUM_ITERATIONS
    )
    
    # Derive the master scret
    master_secret = kdf.derive(pre_master_secret_bytes)
    return master_secret
def generate_enc_and_MAC_key(master_secret: bytes, pre_master_secret: bytes):
    # use the first 16 bytes of pre master secret as salt for our keys to ensure they are symmetric
    pre_master_salt = pre_master_secret[:16]
    aes_kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  
        salt=pre_master_salt,
        iterations=NUM_ITERATIONS
    )

    MAC_kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes for HMAC-SHA256
        salt=pre_master_salt,
        iterations=NUM_ITERATIONS
    )

    AES_encryption_key = aes_kdf.derive(master_secret)
    MAC_key = MAC_kdf.derive(master_secret)
    return AES_encryption_key, MAC_key

def secure_receive(message_json: dict, ENC_KEY: bytes, MAC_KEY: bytes) -> dict:
    iv = bytes.fromhex(message_json["iv"])
    ciphertext = bytes.fromhex(message_json["ciphertext"])
    received_mac = message_json["mac"]

    expected_mac = hmac.new(MAC_KEY, iv + ciphertext, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(received_mac, expected_mac):
        raise Exception("MAC verification failed!")

    plaintext = decrypt_with_AES_key(ciphertext, ENC_KEY, iv)

    return json.loads(plaintext)


def secure_send(response_dict: dict, ENC_KEY: bytes, MAC_KEY: bytes) -> dict:
    iv = secrets.token_bytes(16)  # 128-bit IV for AES-CBC

    plaintext = json.dumps(response_dict)

    ciphertext = encrypt_with_AES_key(plaintext, ENC_KEY, iv)

    mac = hmac.new(MAC_KEY, iv + ciphertext, hashlib.sha256).hexdigest()

    return {
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex(),
        "mac": mac
    }