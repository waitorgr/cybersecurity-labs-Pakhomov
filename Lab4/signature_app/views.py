import hashlib
from django.shortcuts import render
from .forms import SignatureForm, VerifyForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse,FileResponse
import io
import os
import math
import random

# Параметри (демонстраційні)
MIN_PRIME = 10007  # мінімальне стартове значення для пошуку простого
DEFAULT_E = 65537  # публічний експонент (зміниться при конфлікті)

# ---- Утиліти для роботи з простими числами / інверсією ----
def is_probable_prime(n, k=5):
    """Miller-Rabin quick primality test (probabilistic)."""
    if n < 2:
        return False
    small_primes = (2,3,5,7,11,13,17,19,23,29)
    for p in small_primes:
        if n % p == 0:
            return n == p
    # write n-1 as d*2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def next_prime(start):
    """Шукає наступне просте число >= start."""
    if start <= 2:
        return 2
    n = start if start % 2 == 1 else start + 1
    while True:
        if is_probable_prime(n):
            return n
        n += 2

def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("modular inverse does not exist")
    return x % m

# ---- Ключі / підпис ----
def generate_rsa_like_keys_from_personal(last_name, birth_date, secret_word):
    """
    Детерміністично генерує пару (n, e, d) з персональних даних.
    Підхід:
      - бере хеш персональних даних, перетворює в число seed
      - шукає два простих числа p, q починаючи від seed-derived offsets
      - обчислює n = p*q, phi = (p-1)*(q-1)
      - намагається взяти e = DEFAULT_E; якщо не взаємно просте з phi, пробує інші прості e
    Повертає (n, e, d). Приватний ключ = d, публічний = (n, e).
    """
    # seed з персональних даних
    raw = f"{last_name}{birth_date.strftime('%d%m%Y')}{secret_word}"
    seed = int(hashlib.sha256(raw.encode()).hexdigest(), 16)
    # створюємо стартові значення для p і q
    start_p = (seed % 100000) + MIN_PRIME
    start_q = ((seed >> 16) % 100000) + MIN_PRIME + 1000

    p = next_prime(start_p)
    q = next_prime(start_q)
    # якщо випадково співпадають, зрушимо q
    if q == p:
        q = next_prime(q + 2)

    n = p * q
    phi = (p - 1) * (q - 1)

    # вибираємо e
    e = DEFAULT_E
    if math.gcd(e, phi) != 1:
        # знайдемо невелике просте e, coprime з phi
        for cand in (3,5,17,257,65537):
            if cand < phi and math.gcd(cand, phi) == 1:
                e = cand
                break
        else:
            # запасний лінійний пошук
            e = 3
            while e < phi and math.gcd(e, phi) != 1:
                e += 2

    # обчислюємо d
    d = modinv(e, phi)
    return n, e, d

# ---- Хеш файлу (підтримка SHA256, SHA512, MD5) ----
def hash_file(file_obj, algorithm='sha256', mod=None):
    """
    file_obj: UploadedFile або відкритий файловий об'єкт
    algorithm: 'sha256'|'sha512'|'md5'
    mod: якщо вказано, повертаємо hash % mod (щоб бути меншим n)
    """
    if algorithm not in hashlib.algorithms_available:
        algorithm = 'sha256'
    h = hashlib.new(algorithm)

    if hasattr(file_obj, 'chunks'):
        for chunk in file_obj.chunks():
            h.update(chunk)
    else:
        # файл відкритий бінарний
        while True:
            data = file_obj.read(8192)
            if not data:
                break
            h.update(data)

    value = int(h.hexdigest(), 16)
    if mod:
        return value % mod
    return value

# ---- Підписування / перевірка (RSA-подібне) ----
def create_signature_rsa_like(file_hash, d, n):
    # підпис: file_hash^d mod n
    return pow(file_hash, d, n)

def verify_signature_rsa_like(file_hash, signature, e, n):
    # перевірка: signature^e mod n == file_hash
    return pow(signature, e, n) == file_hash

# ---- Views ----
def index(request):
    if request.method == "POST":
        form = SignatureForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.cleaned_data['document']
            hash_algorithm = form.cleaned_data['hash_algorithm']

            # Зберігаємо файл у media/temp/
            fs = FileSystemStorage(location='media/temp')
            filename = fs.save(document.name, document)
            document_path = fs.path(filename)

            # Генеруємо ключі з персональних даних (server-side)
            last_name = form.cleaned_data['last_name']
            birth_date = form.cleaned_data['birth_date']
            secret_word = form.cleaned_data['secret_word']

            n, e, d = generate_rsa_like_keys_from_personal(last_name, birth_date, secret_word)

            # обчислюємо хеш файлу модулем n (щоб file_hash < n)
            with open(document_path, 'rb') as f:
                file_hash = hash_file(f, hash_algorithm, mod=n)

            signature = create_signature_rsa_like(file_hash, d, n)

            is_valid = verify_signature_rsa_like(file_hash, signature, e, n)

            # ЗАУВАЖ: приватний ключ d **не** кладемо в context
            context = {
                'public_n': n,
                'public_e': e,
                'file_hash': file_hash,
                'signature': signature,
                'hash_algorithm': hash_algorithm,
                'is_valid': is_valid,
                'document_path': document_path,
                'filename': filename
            }
            return render(request, 'result.html', context)
    else:
        form = SignatureForm()
    return render(request, 'index.html', {'form': form})

def verify_view(request):
    message = None
    if request.method == "POST":
        form = VerifyForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.cleaned_data['document']
            public_n = form.cleaned_data['public_n']
            public_e = form.cleaned_data['public_e']
            signature = form.cleaned_data['signature']
            hash_algorithm = form.cleaned_data['hash_algorithm']

            # обчислюємо хеш файлу модулем n (щоб узгоджуватися з підписом)
            file_hash = hash_file(document, hash_algorithm, mod=public_n)

            is_valid = verify_signature_rsa_like(file_hash, signature, public_e, public_n)
            message = "Підпис ДІЙСНИЙ" if is_valid else "Підпис ПІДРОБЛЕНИЙ"
    else:
        form = VerifyForm()
    return render(request, 'verify.html', {'form': form, 'message': message})


def download_signed_document(request):
    document_path = request.GET.get('document_path')
    if not document_path or not os.path.exists(document_path):
        return HttpResponse("Файл не знайдено", status=404)

    # Віддаємо саме файл, без змін
    response = FileResponse(open(document_path, 'rb'), as_attachment=True)
    
    # Встановлюємо ім'я файлу
    base, ext = os.path.splitext(os.path.basename(document_path))
    out_name = f"{base}_signed{ext or '.bin'}"
    response['Content-Disposition'] = f'attachment; filename="{out_name}"'
    return response
