import os
import base64
import json
import hashlib
from cryptography.fernet import Fernet

def get_machine_id():
    """Generates a unique ID based on machine hardware."""
    try:
        # Try to get unique machine ID from system files
        if os.path.exists("/etc/machine-id"):
            with open("/etc/machine-id", "r") as f:
                return f.read().strip()
        elif os.path.exists("/var/lib/dbus/machine-id"):
            with open("/var/lib/dbus/machine-id", "r") as f:
                return f.read().strip()
        else:
            # Fallback to hostname if IDs are missing
            import socket
            return socket.gethostname()
    except:
        return "fallback-unique-id-zade"

def generate_key():
    """Derives a Fernet key from the machine ID."""
    machine_id = get_machine_id()
    # Use SHA-256 to create a 32-byte key from the variable machine_id
    key = hashlib.sha256(machine_id.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_data(data_dict):
    """Encrypts a dictionary into a byte string."""
    key = generate_key()
    f = Fernet(key)
    json_data = json.dumps(data_dict).encode()
    return f.encrypt(json_data)

def decrypt_data(encrypted_bytes):
    """Decrypts byte string into a dictionary."""
    key = generate_key()
    f = Fernet(key)
    try:
        decrypted_data = f.decrypt(encrypted_bytes)
        return json.loads(decrypted_data.decode())
    except:
        return None

def save_secure_config(config_path, data):
    """Saves config as an encrypted file."""
    encrypted_bytes = encrypt_data(data)
    with open(config_path, "wb") as f:
        f.write(encrypted_bytes)

def load_secure_config(config_path):
    """Loads config, decrypting if necessary. Supports migration from plain text."""
    if not os.path.exists(config_path):
        return None
        
    try:
        # Attempt to read as binary/encrypted
        with open(config_path, "rb") as f:
            raw_data = f.read()
            
        # Try to decrypt
        decrypted = decrypt_data(raw_data)
        if decrypted:
            return decrypted
            
        # If decryption fails, maybe it's plain text (old format)?
        # Let's try to parse it as plain JSON
        with open(config_path, "r") as f:
            return json.load(f)
    except:
        return None
