import pytest
from protector.pipeline import sign, encrypt, stego
from PIL import Image

def test_sign_encrypt_stego_roundtrip(tmp_path):
    # генерація ключів
    priv, pub = sign.generate_keys(priv_path=str(tmp_path/'priv.pem'), pub_path=str(tmp_path/'pub.pem'))
    data = b'hello world'*100

    # підпис
    sig, t = sign.sign_data(data, priv_key_path=priv)
    package = sig + data

    # шифрування
    enc = encrypt.aes_gcm_encrypt(package, password='testpass')
    cipher = enc['ciphertext']

    # створити cover image
    img_path = tmp_path/'cover.png'
    Image.new('RGB', (200,200), color=(255,255,255)).save(img_path)

    # вставка стего
    out = tmp_path/'container.png'
    stego.embed_lsb(str(img_path), cipher, str(out))

    # витяг payload
    extracted = stego.extract_lsb(str(out))

    # дешифрування
    pt = encrypt.aes_gcm_decrypt(extracted, enc['nonce'], password='testpass', salt=enc['salt'])
    assert pt.startswith(sig)
