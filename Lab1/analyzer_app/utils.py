import re
import string

def check_personal_data(password, name, birth_date):
    """Перевірка пароля на наявність персональних даних"""
    found = []
    if name.lower() in password.lower():
        found.append("name")  # Ім'я знайдено у паролі
    year = birth_date.split(".")[-1]
    if year in password:
        found.append("birth_date")  # Рік народження знайдено у паролі
    return found

def evaluate_strength(password):
    """Обчислення оцінки пароля від 0 до 100"""
    score = 0
    length = len(password)

    # Основні характеристики пароля
    upper = sum(1 for c in password if c.isupper())  # Кількість великих літер
    lower = sum(1 for c in password if c.islower())  # Кількість малих літер
    digits = sum(1 for c in password if c.isdigit())  # Кількість цифр
    symbols = sum(1 for c in password if c in string.punctuation)  # Кількість символів
    middle = sum(1 for c in password[1:-1] if c.isdigit() or c in string.punctuation)  # Цифри або символи всередині пароля

    # Додавання балів за основні характеристики
    score += length * 4
    score += upper * 2 if upper else 0
    score += lower * 2 if lower else 0
    score += digits * 4
    score += symbols * 6
    score += middle * 2

    # Вимоги до пароля
    requirements = 0
    if length >= 8: requirements += 1  # Довжина >= 8
    if upper > 0: requirements += 1  # Є великі літери
    if lower > 0: requirements += 1  # Є малі літери
    if digits > 0: requirements += 1  # Є цифри
    if symbols > 0: requirements += 1  # Є символи
    if requirements >= 4:
        score += requirements * 2  # Додаткові бали за виконання вимог

    # Вирахування балів за недоліки
    letters_only = length == (upper + lower)  # Лише літери
    numbers_only = length == digits  # Лише цифри
    repeat_chars = sum(password.lower().count(c) - 1 for c in set(password.lower()))  # Повторення символів
    consecutive_upper = sum(1 for i in range(len(password)-1) if password[i].isupper() and password[i+1].isupper())  # Послідовні великі літери
    consecutive_lower = sum(1 for i in range(len(password)-1) if password[i].islower() and password[i+1].islower())  # Послідовні малі літери
    consecutive_digits = sum(1 for i in range(len(password)-1) if password[i].isdigit() and password[i+1].isdigit())  # Послідовні цифри

    score -= letters_only * length
    score -= numbers_only * length
    score -= repeat_chars
    score -= consecutive_upper * 2
    score -= consecutive_lower * 2
    score -= consecutive_digits * 2

    # Послідовності букв, цифр, символів
    seq_letters = sum(1 for i in range(len(password)-2) if password[i:i+3].lower() in string.ascii_lowercase)
    seq_numbers = sum(1 for i in range(len(password)-2) if password[i:i+3] in '0123456789')
    seq_symbols = sum(1 for i in range(len(password)-2) if password[i:i+3] in "!@#$%^&*()")

    score -= (seq_letters + seq_numbers + seq_symbols) * 3

    # Нормалізація оцінки до 0-100
    score = max(0, min(100, score))
    return score

def get_recommendations(password, personal_data_matches, score):
    """Генерація рекомендацій на основі оцінки пароля"""
    recommendations = []
    if personal_data_matches:
        recommendations.append("Уникайте використання особистих даних у паролі.")
    if len(password) < 8:
        recommendations.append("Зробіть пароль довшим (мінімум 8 символів).")
    if not any(c.isupper() for c in password):
        recommendations.append("Додайте великі літери.")
    if not any(c.islower() for c in password):
        recommendations.append("Додайте малі літери.")
    if not any(c.isdigit() for c in password):
        recommendations.append("Додайте цифри.")
    if not any(c in string.punctuation for c in password):
        recommendations.append("Додайте спеціальні символи.")
    if score >= 80 and not personal_data_matches:
        recommendations.append("Пароль виглядає дуже надійним.")
    elif score >= 60:
        recommendations.append("Пароль середньої надійності, можна покращити.")
    else:
        recommendations.append("Пароль слабкий, варто змінити.")
    return recommendations
