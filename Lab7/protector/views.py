import os
import base64
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import UploadForm
from .models import FileRecord
from .pipeline import sign as sign_mod, encrypt as enc_mod, stego as stego_mod, analytics as analytics_mod, utils as utils_mod
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
import time
import struct
from django.http import HttpResponse
from base64 import b64decode

def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES.get('file')
            text = form.cleaned_data.get('text')
            cover = request.FILES['cover_image']
            password = form.cleaned_data.get('password') or "1234"  # тестовий пароль

            # -----------------------
            # Створюємо запис в базі
            rec = FileRecord.objects.create(original_name=f.name if f else "text_input")

            # Отримуємо байти для обробки
            if f:
                orig_bytes = f.read()
                rec = FileRecord.objects.create(
                    original_name=f.name,
                    size_original=len(orig_bytes)
                )
                rec.uploaded_file.save(f.name, f)
            else:
                orig_bytes = text.encode('utf-8')
                rec = FileRecord.objects.create(
                    original_name="text_input.txt",
                    size_original=len(orig_bytes)
                )

            # -----------------------
            # 1) Підпис
            signature_with_len, t_sign = sign_mod.sign_data(orig_bytes)
            rec.time_sign_ms = round(t_sign, 3)
            rec.signature_bytes = signature_with_len  # зберігаємо в DB
            package = signature_with_len + orig_bytes

            # -----------------------
            # 2) Шифрування AES-GCM
            enc = enc_mod.aes_gcm_encrypt(package, password=password)
            cipher = enc['ciphertext']
            rec.time_encrypt_ms = enc['time_ms']
            rec.size_cipher = len(cipher)
            rec.cipher_bytes = cipher  # зберігаємо в DB
            rec.nonce = enc['nonce']
            rec.salt = enc['salt']
            rec.save()

            # -----------------------
            # 3) Стеганографія
            nonce = enc['nonce'] or b''
            salt = enc['salt'] or b''
            cipher = enc['ciphertext']

            payload = (len(nonce)).to_bytes(2, 'big') + nonce + (len(salt)).to_bytes(2, 'big') + salt + cipher

            # Готуємо cover
            cover_path = os.path.join(settings.MEDIA_ROOT, cover.name)
            with open(cover_path, 'wb') as cf:
                for chunk in cover.chunks():
                    cf.write(chunk)

            out_container = os.path.join(settings.MEDIA_ROOT, f"container_{rec.id}.png")

            # Вимірюємо час стего
            import time
            start_stego = time.time()
            stego_mod.embed_lsb(cover_path, payload, out_container)
            end_stego = time.time()

            rec.container_image.name = os.path.relpath(out_container, settings.MEDIA_ROOT)
            rec.time_stego_ms = (end_stego - start_stego) * 1000.0
            rec.size_container = os.path.getsize(out_container)

            # Зберігаємо також у базі (опціонально) cipher/signature
            rec.signature_bytes = signature_with_len
            rec.cipher_bytes = cipher
            rec.password = password 
            rec.save()

            # -----------------------
            # Аналітика
            analytics_mod.append_csv_row(os.path.join(settings.BASE_DIR, 'analytics.csv'), {
                'timestamp': datetime.now().isoformat(),
                'file_id': rec.id,
                'size_original': rec.size_original,
                'size_cipher': rec.size_cipher,
                'size_container': rec.size_container,
                'time_sign_ms': rec.time_sign_ms,
                'time_encrypt_ms': rec.time_encrypt_ms,
                'time_stego_ms': rec.time_stego_ms,
                'success_restore': False,
                'signature_valid': False
            })

            # -----------------------
            # Відновлення та перевірка підпису
            try:
                restored_data, valid_sig = utils_mod.restore_and_verify(
                    rec.container_image.path,
                    password=rec.password  # <-- обов'язково реальний пароль з DB
                )
                rec.success_restore = True
                rec.signature_valid = valid_sig
            except Exception:
                rec.success_restore = False
                rec.signature_valid = False
                
            rec.save()

            return redirect('protector:encrypt_data', pk=rec.id)

    else:
        form = UploadForm()
    return render(request, 'protector/upload.html', {'form': form})


def status_view(request, pk):
    rec = get_object_or_404(FileRecord, pk=pk)

    signature_valid = False

    try:
        # Витягуємо payload із контейнера (як у decrypt_data_view)
        payload = stego_mod.extract_lsb(os.path.join(settings.MEDIA_ROOT, rec.container_image.name))
        idx = 0
        nonce_len = int.from_bytes(payload[idx:idx+2], 'big'); idx += 2
        nonce = payload[idx:idx+nonce_len]; idx += nonce_len
        salt_len = int.from_bytes(payload[idx:idx+2], 'big'); idx += 2
        salt = payload[idx:idx+salt_len]; idx += salt_len
        cipher = payload[idx:]

        # Дешифрування AES-GCM
        package = enc_mod.aes_gcm_decrypt(cipher, password=rec.password, nonce=nonce, salt=salt)

        # Витяг підпису та даних
        sig_len = int.from_bytes(package[:2], 'big')
        signature = package[2:2+sig_len]
        data = package[2+sig_len:]

        # Перевірка підпису
        pub_key_path = os.path.join(settings.BASE_DIR, "keys/ecdsa_pub.pem")
        with open(pub_key_path, "rb") as f:
            pub_key = serialization.load_pem_public_key(f.read())
        pub_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        signature_valid = True
    except Exception:
        signature_valid = False

    rec.signature_valid = signature_valid
    rec.save()

    return render(request, 'protector/status.html', {'rec': rec})



def encrypt_data_view(request, pk):
    rec = get_object_or_404(FileRecord, pk=pk)

    context = {
        "rec": rec,
        "original_name": rec.original_name,
        "size_original": rec.size_original,
        "container_url": rec.container_image.url if rec.container_image else None,
    }
    return render(request, "protector/encrypt_data.html", context)



def decrypt_data_view(request, pk=None):
    decrypted_text = ""
    signature_valid = None
    error_msg = ""
    download_file = None
    download_name = None

    # якщо передано pk — намагаємось отримати запис, щоб мати original_name
    rec = None
    if pk:
        rec = get_object_or_404(FileRecord, pk=pk)

    if request.method == "POST":
        # або беремо файл-контейнер з форми, або Base64 поля з форми
        uploaded_container = request.FILES.get('container_file')
        container_path = None

        if uploaded_container:
            # зберігаємо тимчасово контейнер у MEDIA для обробки
            tmp_name = f"tmp_container_{int(time.time()*1000)}.png"
            container_path = os.path.join(settings.MEDIA_ROOT, tmp_name)
            with open(container_path, 'wb') as wf:
                for chunk in uploaded_container.chunks():
                    wf.write(chunk)
        else:
            # або беремо існуючий контейнер з DB (якщо pk вказаний)
            if rec and rec.container_image:
                container_path = os.path.join(settings.MEDIA_ROOT, rec.container_image.name)

        password = request.POST.get('password') or None

        try:
            # 1) Екстракт payload з контейнера
            payload = stego_mod.extract_lsb(container_path)

            # 2) Розбір payload: 2B nonce_len, nonce, 2B salt_len, salt, rest=cipher
            idx = 0
            nonce_len = int.from_bytes(payload[idx:idx+2], 'big'); idx += 2
            nonce = payload[idx:idx+nonce_len]; idx += nonce_len
            salt_len = int.from_bytes(payload[idx:idx+2], 'big'); idx += 2
            salt = payload[idx:idx+salt_len]; idx += salt_len
            cipher = payload[idx:]

            # 3) Дешифрування AES-GCM (отримуємо package = signature_with_len + data)
            package = enc_mod.aes_gcm_decrypt(ciphertext=cipher, nonce=nonce, password=password, salt=salt)

            # 4) Витяг підпису і даних з package
            sig_len = int.from_bytes(package[:2], 'big')
            signature = package[2:2+sig_len]
            data = package[2+sig_len:]

            # 5) Перевірка підпису
            pub_key_path = os.path.join(settings.BASE_DIR, "keys/ecdsa_pub.pem")
            with open(pub_key_path, "rb") as f:
                pub_key = serialization.load_pem_public_key(f.read())
            try:
                pub_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
                signature_valid = True
            except Exception:
                signature_valid = False

            # 6) Визначення чи це текст чи файл
            try:
                decrypted_text = data.decode('utf-8')
            except Exception:
                download_file = data
                # ім'я беремо з rec, якщо є, інакше робимо дефолт з розширення (спроба вгадати не робимо)
                download_name = rec.original_name if rec and rec.original_name else "restored_file"

        except Exception as e:
            error_msg = str(e)
            signature_valid = False
            decrypted_text = ""

    # Якщо потрібно віддати файл для скачування
    if download_file:
        response = HttpResponse(download_file, content_type="application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{download_name}"'
        return response

    return render(request, "protector/decrypt_data.html", {
        "decrypted_text": decrypted_text,
        "signature_valid": signature_valid,
        "error_msg": error_msg,
    })