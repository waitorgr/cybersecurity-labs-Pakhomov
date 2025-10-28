# Steganography Django Project

Проєкт дозволяє приховувати текстові повідомлення у зображеннях за допомогою методу LSB (Least Significant Bit) і потім витягати їх назад.

## Особливості
- Приховування повідомлень у зображеннях формату PNG/JPG.
- Можливість використання ключа для XOR-шифрування.
- Можливість вибору каналів (R, G, B) для приховування.
- Відображення аналітики: розмір зображення, кількість змінених пікселів.

## Встановлення

1. Клонувати репозиторій:

```bash
git clone https://github.com/waitorgr/cybersecurity-labs-Pakhomov.git
cd steganography-django
Створити та активувати віртуальне середовище:
```
```bash
python -m venv env
env\Scripts\activate   # Windows
# або для Linux/Mac:
# source env/bin/activate
```

Встановити залежності:
```bash
pip install -r requirements.txt
```

Налаштувати Django:

```bash
python manage.py migrate
python manage.py createsuperuser  # за бажанням
python manage.py runserver
```
Відкрити в браузері:
```bash
http://127.0.0.1:8000/
```
# Використання
Hide message – завантажуєте зображення, вводите повідомлення, ключ (за бажанням) і натискаєте "Hide".

Extract message – завантажуєте зображення з прихованим повідомленням і вводите ключ (якщо використовувався).