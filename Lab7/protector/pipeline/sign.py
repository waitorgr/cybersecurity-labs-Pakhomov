import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

# Генерація ключів
def generate_keys(priv_path='keys/ecdsa_priv.pem', pub_path='keys/ecdsa_pub.pem'):
    private_key = ec.generate_private_key(ec.SECP256R1())
    priv_bytes = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    )
    with open(priv_path, 'wb') as f:
        f.write(priv_bytes)
    pub = private_key.public_key()
    pub_bytes = pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    with open(pub_path, 'wb') as f:
        f.write(pub_bytes)
    return priv_path, pub_path

# Підписування даних
def sign_data(data: bytes, priv_key_path='keys/ecdsa_priv.pem'):
    with open(priv_key_path, 'rb') as f:
        priv_key = serialization.load_pem_private_key(f.read(), password=None)
    
    start = time.time()
    signature = priv_key.sign(data, ec.ECDSA(hashes.SHA256()))
    end = time.time()
    time_ms = (end - start) * 1000
    
    # Додаємо довжину підпису (2 байти) на початок
    signature_len_bytes = len(signature).to_bytes(2, 'big')
    return signature_len_bytes + signature, time_ms
