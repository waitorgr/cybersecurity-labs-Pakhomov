import os, time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def derive_key_from_password(password: str, salt: bytes=None):
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000)
    key = kdf.derive(password.encode())
    return key, salt

def aes_gcm_encrypt(plaintext: bytes, key: bytes=None, password: str=None):
    start = time.time()
    if key is None and password is None:
        raise ValueError("Provide key or password")
    if key is None:
        key, salt = derive_key_from_password(password)
    else:
        salt = None
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    end = time.time()
    return {
        'ciphertext': ct,
        'nonce': nonce,
        'salt': salt,
        'time_ms': (end - start) * 1000.0
    }

def aes_gcm_decrypt(ciphertext: bytes, nonce: bytes, key: bytes=None, password: str=None, salt: bytes=None):
    if key is None:
        key, _ = derive_key_from_password(password, salt)
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ciphertext, None)
    return pt
