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
curl -i "http://127.0.0.1:8000/search/vulnerable/?q=%25%27%20OR%20%271%27%3D%271"
curl -i "http://127.0.0.1:8000/search/safe/?q=%25%27%20OR%20%271%27%3D%271"
```

---

## Що демонструє проект

1. **Vulnerable** (`/search/vulnerable/`) — ручна конкатенація user input у SQL:

   ```python
   raw_sql = f"SELECT id, name, email, secret_info FROM demoapp_person WHERE name LIKE '%{query}%'"
   cursor.execute(raw_sql)
   ```

   Результат: ін’єкція змінює логіку запиту → можливий витік даних.

2. **Safe** (`/search/safe/`) — ORM або параметризований запит:

   ```python
   results_qs = Person.objects.filter(name__icontains=query)
   ```

   Результат: введені дані трактуються як дані, не як частина SQL‑структури → ін’єкція не працює.

---

## Що фіксувати для звіту (інструкція для ЛР)

Під час тестування зафіксуйте:

* URL та payload
* Як відправляли (браузер / Burp / curl)
* HTTP статус відповіді
* Уривок тіла відповіді (200–300 символів) або скріншоти
* Текст помилок (якщо з’явилися): з шаблону `error` на сторінці або з консолі `runserver`
* Висновок: чи відбувся витік даних

Приклад таблиці (для звіту):

| Test payload   | Vulnerable — observed                                | Safe — observed                                                       |
| -------------- | ---------------------------------------------------- | --------------------------------------------------------------------- |
| `%' OR '1'='1` | 200 OK; повернуто всі записи з `secret_info` (витік) | 200 OK; no results або лише буквальний збіг; `secret_info` не витікає |

---

## Логування та додаткові експерименти

* Можна додати логування запитів/спроб (middleware або окремий лог у views) — корисно для демонстрації спроб атаки.
* Додати варіанти з login bypass (форми логіну) для демонстрації подібних паттернів.
* При тестуванні UNION / time‑based / error‑based ін’єкцій — будьте обережні і працюйте лише локально.

---

## Відомі обмеження

* Проєкт призначений для навчання — DEBUG=True, sqlite3, мінімальна обробка помилок.
* Не використовувати у продакшн.
* Деякі payload‑и можуть поводитися по‑різному залежно від СУБД (SQLite vs PostgreSQL vs MySQL). При переносі на іншу БД змінюються плейсхолдери та синтаксис.

---

## Посилання

* PortSwigger Web Security Academy — SQL Injection: [https://portswigger.net/web-security/sql-injection](https://portswigger.net/web-security/sql-injection)
* Репозиторій автора: [https://github.com/waitorgr/cybersecurity-labs-Pakhomov.git](https://github.com/waitorgr/cybersecurity-labs-Pakhomov.git)

---

## Ліцензія

Проєкт доступний для навчального використання. Ви можете вільно вивчати код і модифікувати його для освітніх цілей. Забороняється використовувати цей код для атаки на сторонні системи без дозволу.

---

### Контакти

Якщо потрібна допомога з розгортанням або додатковими прикладами — відпишіть у issues репозиторію або зв’яжіться зі мною через GitHub.
