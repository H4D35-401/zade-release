import json
import os
import logging
from secure_io import load_secure_config, save_secure_config

logger = logging.getLogger(__name__)

# Path based on runtime environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_PATH = os.path.join(BASE_DIR, "memory.json")

def load_memory():
    """Loads long-term memory for the AI."""
    mem = load_secure_config(MEMORY_PATH)
    if mem:
        return mem
    return {
        "user_name": "Sir",
        "zade_name": "ZADE",
        "preferences": {
            "personality": "concise, witty, and tactical",
            "interests": []
        },
        "session_history": []
    }

def update_memory(data):
    """Saves updated memory to the encrypted file."""
    try:
        current = load_memory()
        current.update(data)
        save_secure_config(MEMORY_PATH, current)
        return True
    except Exception as e:
        logger.error(f"Memory sync failure: {e}")
        return False

def get_identity_context():
    """Returns a string describing the current user identity."""
    mem = load_memory()
    return f"You are speaking with {mem['user_name']}. Your name is {mem['zade_name']}. Your personality is {mem['preferences']['personality']}."
