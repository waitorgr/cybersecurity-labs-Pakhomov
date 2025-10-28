import string
from typing import List, Dict, Tuple
from collections import Counter


def caesar_encrypt(text, shift):
    """
    Зашифрувати текст шифром Цезаря
    :param text: рядок для шифрування
    :param shift: зсув (ціле число)
    :return: зашифрований рядок
    """
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result


def caesar_decrypt(text, shift):
    """
    Розшифрувати текст шифром Цезаря
    :param text: зашифрований рядок
    :param shift: зсув (той самий, що при шифруванні)
    :return: розшифрований рядок
    """
    return caesar_encrypt(text, -shift)


def xor_encrypt(message: str, key: int) -> bytes:
    """
    Зашифрувати текст XOR-шифром
    :param message: рядок для шифрування
    :param key: ключ (ціле число 0-255)
    :return: зашифровані байти
    """
    message_bytes = message.encode('utf-8')
    encrypted = bytes([b ^ key for b in message_bytes])
    return encrypted

def xor_decrypt(encrypted_message: bytes, key: int) -> str:
    """
    Розшифрувати XOR-шифр
    :param encrypted_message: байти зашифрованого тексту
    :param key: той самий ключ, що при шифруванні
    :return: розшифрований рядок
    """
    decrypted_bytes = bytes([b ^ key for b in encrypted_message])
    return decrypted_bytes.decode('utf-8')


# Український алфавіт (маленькі літери). Додаємо 'ґ','є','і','ї'
UKR_ALPHABET = list("абвгґдеєжзиіїйклмнопрстуфхцчшщьюя")
ENG_ALPHABET = list(string.ascii_lowercase)


def detect_alphabet(text: str) -> Tuple[List[str], str]:
    """
    Визначаємо, який алфавіт використовувати: 'ukr' або 'eng'.
    Якщо в тексті є кирилиця -> 'ukr', інакше 'eng'.
    Повертаємо (alphabet_list, name).
    """
    if any('\u0400' <= ch <= '\u04FF' for ch in text):  # кириличні діапазони
        return UKR_ALPHABET, 'ukr'
    else:
        return ENG_ALPHABET, 'eng'


def caesar_shift_char(ch: str, shift: int, alphabet: List[str]) -> str:
    """
    Зсуває символ ch у даному алфавіті на shift позицій.
    Якщо символ не у алфавіті — повертає як є.
    Зберігає регістр.
    """
    lower = ch.lower()
    if lower in alphabet:
        idx = alphabet.index(lower)
        new_idx = (idx + shift) % len(alphabet)
        res = alphabet[new_idx]
        return res.upper() if ch.isupper() else res
    return ch


def caesar_encrypt_with_alphabet(text: str, shift: int, alphabet: List[str]) -> str:
    return ''.join(caesar_shift_char(ch, shift, alphabet) for ch in text)


def caesar_bruteforce(ciphertext: str) -> List[Dict]:
    """
    Перебирає всі можливі зсуви для відповідного алфавіту і повертає список варіантів.
    Кожен елемент: {'shift': int, 'plaintext': str}
    """
    alphabet, name = detect_alphabet(ciphertext)
    results = []
    for s in range(len(alphabet)):
        pt = caesar_encrypt_with_alphabet(ciphertext, s, alphabet)
        results.append({'shift': s, 'plaintext': pt})
    return results


def frequency_analysis(ciphertext: str) -> Dict:
    """
    Рахує частоти літер у ciphertext (літери алфавіту).
    Повертає структуру:
    {
      'alphabet_name': 'ukr' or 'eng',
      'labels': [...letters...],
      'counts': [...],
      'percent': [...],
      'most_common': ('о', 123)  # приклад
    }
    """
    alphabet, name = detect_alphabet(ciphertext)
    text_lower = ''.join(ch.lower() for ch in ciphertext)
    # Відфільтруємо лише літери з алфавіту
    letters = [ch for ch in text_lower if ch in alphabet]
    counter = Counter(letters)
    total = sum(counter.values()) if counter else 0

    labels = alphabet
    counts = [counter.get(ch, 0) for ch in labels]
    percent = [round((c / total) * 100, 2) if total > 0 else 0 for c in counts]
    most_common = counter.most_common(1)[0] if counter else (None, 0)

    return {
        'alphabet_name': name,
        'labels': labels,
        'counts': counts,
        'percent': percent,
        'most_common': most_common,
        'total_letters': total
    }


def suggest_shifts_by_frequency(ciphertext: str, common_plain_letter: str = None) -> List[Dict]:
    """
    Пропозиції зсувів на основі частот: вирівнюємо найчастішу літеру ciphertext
    до common_plain_letter (за замовчуванням: 'e' для англ. або 'о' для укр. — але це можна задати).
    Повертає список пропозицій [{'shift': int, 'mapped_from': 'x', 'map_to': 'e', 'plaintext': '...'}, ...]
    """
    alphabet, name = detect_alphabet(ciphertext)
    freq = frequency_analysis(ciphertext)
    most_common_letter = freq['most_common'][0]
    if not most_common_letter:
        return []

    if common_plain_letter is None:
        # за замовчуванням
        common_plain_letter = 'о' if name == 'ukr' else 'e'

    suggestions = []
    # якщо most_common_letter вже одна з alphabet
    for target in (common_plain_letter,):
        # знайдемо зсув, який переводить most_common_letter -> target
        if most_common_letter in alphabet and target in alphabet:
            from_idx = alphabet.index(most_common_letter)
            to_idx = alphabet.index(target)
            shift = (to_idx - from_idx) % len(alphabet)
            plaintext = caesar_encrypt_with_alphabet(ciphertext, shift, alphabet)
            suggestions.append({
                'shift': shift,
                'mapped_from': most_common_letter,
                'map_to': target,
                'plaintext': plaintext
            })
    return suggestions

EN_FREQ_ORDER = " etaoinshrdlcumwfgypbvkjxqz"  # приблизний порядок частоти букв англійської

def score_english(text: str) -> float:
    """Проста оцінка англійського тексту."""
    score = 0.0
    text_lower = text.lower()
    for ch in EN_FREQ_ORDER:
        score += text_lower.count(ch) * (len(EN_FREQ_ORDER) - EN_FREQ_ORDER.index(ch))
    non_print = sum(1 for c in text if c not in string.printable)
    score -= non_print * 50
    score += text.count(' ') * 2
    return score

def xor_bruteforce(cipher_bytes: bytes, top_n: int = 10):
    """
    Brute-force для однобайтового XOR.
    Повертає список топ-N кандидатів: (ключ:int, plaintext:str, score:float)
    """
    candidates = []
    for k in range(256):
        try:
            pt = bytes([b ^ k for b in cipher_bytes]).decode('utf-8', errors='strict')
        except UnicodeDecodeError:
            pt = bytes([b ^ k for b in cipher_bytes]).decode('latin1', errors='replace')
        sc = score_english(pt)
        candidates.append((k, pt, sc))
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates

