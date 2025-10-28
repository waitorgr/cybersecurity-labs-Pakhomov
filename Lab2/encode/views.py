# views.py
from django.shortcuts import render
from .utilites import xor_encrypt, xor_decrypt, caesar_encrypt, caesar_decrypt, caesar_bruteforce, frequency_analysis, suggest_shifts_by_frequency, xor_bruteforce
import hashlib
from django.utils.safestring import mark_safe
import json

def analyze_view(request):
    """
    Рендерить сторінку аналізу: brute-force та частотний аналіз.
    На POST робить вибрану операцію і повертає дані для графіку.
    Додано режим 'xor_bruteforce' — перебір однобайтового XOR.
    """
    context = {
        'ciphertext': '',
        'mode': 'bruteforce',  # 'bruteforce', 'frequency', або 'xor_bruteforce'
        'bruteforce_results': None,
        'freq_data_json': None,
        'suggestions': None,
        'xor_bruteforce_results': None,  # для результатів XOR
        'error': None,
    }

    if request.method == 'POST':
        ciphertext = request.POST.get('ciphertext', '')
        mode = request.POST.get('mode', 'bruteforce')
        context['ciphertext'] = ciphertext
        context['mode'] = mode

        if not ciphertext:
            context['error'] = 'Введіть текст для аналізу.'
            return render(request, 'analyze.html', context)

        # ---------- Caesar brute-force ----------
        if mode == 'bruteforce':
            results = caesar_bruteforce(ciphertext)
            context['bruteforce_results'] = results

            # Для зручності також підготуємо частотні дані (щоб можна було переключитись)
            freq = frequency_analysis(ciphertext)
            context['freq_data_json'] = mark_safe(json.dumps({
                'labels': freq['labels'],
                'counts': freq['counts'],
                'percent': freq['percent'],
                'total_letters': freq['total_letters'],
            }, ensure_ascii=False))

        # ---------- Frequency analysis ----------
        elif mode == 'frequency':
            freq = frequency_analysis(ciphertext)
            context['freq_data_json'] = mark_safe(json.dumps({
                'labels': freq['labels'],
                'counts': freq['counts'],
                'percent': freq['percent'],
                'total_letters': freq['total_letters'],
                'most_common': freq['most_common'],
            }, ensure_ascii=False))
            # Пропозиції по зсуву (на основі найчастішої літери)
            suggestions = suggest_shifts_by_frequency(ciphertext)
            context['suggestions'] = suggestions

        # ---------- XOR brute-force (single-byte) ----------
        elif mode == 'xor_bruteforce':
            # Спробуємо інтерпретувати ciphertext як hex; якщо не вийде — візьмемо raw bytes (utf-8)
            cipher_bytes = None
            try:
                # видаляємо пробіли та 0x префікси, якщо є
                hex_str = ciphertext.replace(" ", "").replace("0x", "")
                cipher_bytes = bytes.fromhex(hex_str)
            except Exception:
                # якщо не hex — беремо байти від рядка (це рідко, але можливо)
                cipher_bytes = ciphertext.encode('utf-8')

            try:
                # отримати топ-10 кандидатів (можеш змінити top_n)
                candidates = xor_bruteforce(cipher_bytes, top_n=10)
                # candidates — список (key:int, plaintext:str, score:float)
                # Зручно передати в шаблон як список словників
                context['xor_bruteforce_results'] = [
                    {'key': k, 'plaintext': pt, 'score': sc} for (k, pt, sc) in candidates
                ]
            except Exception as e:
                context['error'] = f'Помилка під час XOR brute-force: {e}'

            # Також підготуємо frequency data для візуалізації (опціонально)
            try:
                freq = frequency_analysis(cipher_bytes.decode('latin1'))  # decode для підрахунку байтових значень
                context['freq_data_json'] = mark_safe(json.dumps({
                    'labels': freq['labels'],
                    'counts': freq['counts'],
                    'percent': freq['percent'],
                    'total_letters': freq['total_letters'],
                }, ensure_ascii=False))
            except Exception:
                # якщо не вдається побудувати частоти — просто пропустимо
                pass

        else:
            context['error'] = 'Невірний режим.'

    return render(request, 'analyze.html', context)
    """
    Рендерить сторінку аналізу: brute-force та частотний аналіз.
    На POST робить вибрану операцію і повертає дані для графіку.
    """
    context = {
        'ciphertext': '',
        'mode': 'bruteforce',  # або 'frequency'
        'bruteforce_results': None,
        'freq_data_json': None,
        'suggestions': None,
        'error': None,
    }

    if request.method == 'POST':
        ciphertext = request.POST.get('ciphertext', '')
        mode = request.POST.get('mode', 'bruteforce')
        context['ciphertext'] = ciphertext
        context['mode'] = mode

        if not ciphertext:
            context['error'] = 'Введіть текст для аналізу.'
            return render(request, 'analyze.html', context)

        if mode == 'bruteforce':
            results = caesar_bruteforce(ciphertext)
            context['bruteforce_results'] = results

            # Для зручності також підготуємо частотні дані (щоб можна було переключитись)
            freq = frequency_analysis(ciphertext)
            context['freq_data_json'] = mark_safe(json.dumps({
                'labels': freq['labels'],
                'counts': freq['counts'],
                'percent': freq['percent'],
                'total_letters': freq['total_letters'],
            }, ensure_ascii=False))

        elif mode == 'frequency':
            freq = frequency_analysis(ciphertext)
            context['freq_data_json'] = mark_safe(json.dumps({
                'labels': freq['labels'],
                'counts': freq['counts'],
                'percent': freq['percent'],
                'total_letters': freq['total_letters'],
                'most_common': freq['most_common'],
            }, ensure_ascii=False))
            # Пропозиції по зсуву (на основі найчастішої літери)
            suggestions = suggest_shifts_by_frequency(ciphertext)
            context['suggestions'] = suggestions

        else:
            context['error'] = 'Невірний режим.'

    return render(request, 'analyze.html', context)


# --- Методи для перетворення DOB на ключі ---
def dob_to_caesar_shift(dob: str, alphabet_len: int = 26) -> int:
    digits = [int(c) for c in dob if c.isdigit()]
    total = sum(digits)
    return total % alphabet_len

def dob_to_xor_key(dob: str) -> int:
    h = hashlib.sha256(dob.encode('utf-8')).digest()
    return h[0]  # перший байт хешу, число від 0 до 255

# --- Основний view ---
def cipher_view(request):
    context = {
        'result': None,
        'text': '',
        'cipher_type': 'caesar',
        'dob': '',
    }

    if request.method == 'POST':
        text = request.POST.get('text', '')
        dob = request.POST.get('dob', '')
        cipher_type = request.POST.get('cipher_type')
        action = request.POST.get('action')
        context.update({'text': text, 'cipher_type': cipher_type, 'dob': dob})

        if not dob:
            context['result'] = 'Введіть дату народження для генерації ключа.'
            return render(request, 'cipher.html', context)

        # --- Caesar ---
        if cipher_type == 'caesar':
            shift = dob_to_caesar_shift(dob, 26)
            if action == 'encrypt':
                context['result'] = caesar_encrypt(text, shift)
            elif action == 'decrypt':
                context['result'] = caesar_decrypt(text, shift)

        # --- XOR ---
        elif cipher_type == 'xor':
            key = dob_to_xor_key(dob)
            if action == 'encrypt':
                encrypted = xor_encrypt(text, key)
                context['result'] = encrypted.hex()
            elif action == 'decrypt':
                try:
                    cipher_bytes = bytes.fromhex(text)
                    context['result'] = xor_decrypt(cipher_bytes, key)
                except Exception as e:
                    context['result'] = f'Помилка розшифрування: {e}'

    return render(request, 'cipher.html', context)
