import os
from . import encrypt, stego, sign
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from django.conf import settings
from . import encrypt as enc


def restore_and_verify(container_path, password):
    payload = stego.extract_lsb(container_path)
    idx = 0
    nonce_len = int.from_bytes(payload[idx:idx+2], 'big'); idx += 2
    nonce = payload[idx:idx+nonce_len]; idx += nonce_len
    salt_len = int.from_bytes(payload[idx:idx+2], 'big'); idx += 2
    salt = payload[idx:idx+salt_len]; idx += salt_len
    cipher = payload[idx:]

    package = enc.aes_gcm_decrypt(cipher, password=password, nonce=nonce, salt=salt)

    sig_len = int.from_bytes(package[:2], 'big')
    signature = package[2:2+sig_len]
    data = package[2+sig_len:]

    # Перевірка підпису
    pub_key_path = os.path.join(settings.BASE_DIR, "keys/ecdsa_pub.pem")
    with open(pub_key_path, "rb") as f:
        pub_key = serialization.load_pem_public_key(f.read())
    pub_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))

    return data, True


