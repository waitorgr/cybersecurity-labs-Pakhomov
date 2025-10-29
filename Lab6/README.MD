# SQLi Demo — Демонстрація SQL‑ін’єкцій (Django)

**Про проєкт**
Цей репозиторій містить простий демонстраційний Django‑застосунок, який показує **вразливу** та **захищену** реалізації функціоналу пошуку по базі персональних даних. Мета — навчитися виявляти SQL‑ін’єкції та продемонструвати, як їх запобігати (параметризовані запити / ORM).

**Важливо — безпека й етика**
Цей код створений тільки в навчальних цілях. Ніколи не застосовуйте вразливі патерни на продакшн‑серверах або без дозволу власника системи. Виконуйте тестування лише у власному локальному середовищі або на виділених навчальних стендах (наприклад PortSwigger Labs).

---

## Зміст репозиторію

```
sqli_demo/
├─ manage.py
├─ sqli_demo/           # Django project (settings, urls)
└─ demoapp/             # Основний додаток
   ├─ models.py         # Модель Person
   ├─ views.py          # search_vulnerable, search_safe
   ├─ templates/        # шаблони: index, search_vulnerable, search_safe
   └─ management/
      └─ commands/
         └─ loaddemo.py # команда для заповнення тестових даних
```

---

## Вимоги

* Python 3.10+ (або 3.8+)
* Django 4.2+
  Рекомендовано: віртуальне оточення (venv).

`requirements.txt`:

```
Django>=4.2
```

---

## Швидкий старт (локально)

1. Склонуйте репозиторій:

```bash
git clone https://github.com/waitorgr/cybersecurity-labs-Pakhomov.git
cd cybersecurity-labs-Pakhomov/sqli_demo
```

2. Створіть та активуйте віртуальне оточення:

```bash
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

3. Встановіть залежності:

```bash
pip install -r requirements.txt
```

4. Міграції та наповнення даних:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddemo
```

5. Запустіть сервер:

```bash
python manage.py runserver
```

6. Відкрийте у браузері:

* Головна: `http://127.0.0.1:8000/`
* Вразливий пошук: `http://127.0.0.1:8000/search/vulnerable/`
* Захищений пошук: `http://127.0.0.1:8000/search/safe/`

---

## Як тестувати (приклади payload‑ів)

В полі `q` (пошук):

* Нормальний приклад:

  * `John` → повертає John Doe
* Wildcard:

  * `%` → (залежно від реалізації LIKE) може повернути всі записи
* Класична SQL‑ін’єкція (для вразливої версії):

  * `%' OR '1'='1`
    У вразливому endpoint це має повернути всі записи, в т.ч. поле `secret_info` (витік).
* Інші варіанти:

  * `' OR '1'='1`
  * `%' UNION SELECT ... --` (експериментально, обережно)

Приклади curl:

```bash
curl -i "http:/
```
