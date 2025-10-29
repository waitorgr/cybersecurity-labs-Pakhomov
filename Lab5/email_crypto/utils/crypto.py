import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend

def derive_fernet_key(personal_string: str, salt: bytes, iterations: int = 200_000) -> bytes:
    """
    Derive a Fernet-compatible key from a personal string (password-like) and salt.
    salt should be stable per user (e.g., email bytes).
    Returns base64 urlsafe-encoded 32-byte key suitable for Fernet.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(personal_string.encode('utf-8'))
    return base64.urlsafe_b64encode(key)

def encrypt_message(plain_text: str, personal_string: str, salt: bytes) -> str:
    key = derive_fernet_key(personal_string, salt)
    f = Fernet(key)
    token = f.encrypt(plain_text.encode('utf-8'))
    # token is bytes, base64 urlsafe already
    return token.decode('utf-8')

def decrypt_message(token_b64: str, personal_string: str, salt: bytes) -> str:
    key = derive_fernet_key(personal_string, salt)
    f = Fernet(key)
    pt = f.decrypt(token_b64.encode('utf-8'))
    return pt.decode('utf-8')

def encrypt_bytes(data: bytes, personal_string: str, salt: bytes) -> bytes:
    key = derive_fernet_key(personal_string, salt)
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_bytes(token: bytes, personal_string: str, salt: bytes) -> bytes:
    key = derive_fernet_key(personal_string, salt)
    f = Fernet(key)
    return f.decrypt(token)
