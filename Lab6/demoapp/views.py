from django.shortcuts import render
from django.db import connection
from .models import Person

def index(request):
    return render(request, "demoapp/index.html")

def search_vulnerable(request):
    """
    Вразлива версія: ручна підстановка user_input у SQL (НЕ РОБИТИ так у продакшні).
    Демонструє SQLi.
    """
    query = request.GET.get("q", "")
    results = []
    error = None
    if query:
        # Тут робиться УЯЗЛИВА конкатенація — навмисно
        raw_sql = f"SELECT id, name, email, secret_info FROM demoapp_person WHERE name LIKE '%{query}%'"
        try:
            with connection.cursor() as cursor:
                cursor.execute(raw_sql)  # vulnerable!
                rows = cursor.fetchall()
                for r in rows:
                    results.append({
                        "id": r[0],
                        "name": r[1],
                        "email": r[2],
                        "secret_info": r[3],
                    })
        except Exception as e:
            error = str(e)  # зберігаємо помилку для логування/демо
    return render(request, "demoapp/search_vulnerable.html", {"query": query, "results": results, "error": error})

def search_safe(request):
    """
    Захищена версія: параметризований запит (плейсхолдер) або використання ORM.
    Тут показано обидва варіанти: ORM (рекомендований) і параметризований raw SQL.
    """
    query = request.GET.get("q", "")
    results = []
    error = None
    if query:
        try:
            # Варіант 1 (рекомендований) — ORM:
            results_qs = Person.objects.filter(name__icontains=query)
            results = list(results_qs.values("id", "name", "email", "secret_info"))
            # Альтернативно, параметризований raw SQL:
            # with connection.cursor() as cursor:
            #     cursor.execute("SELECT id,name,email,secret_info FROM demoapp_person WHERE name LIKE ?", [f"%{query}%"])
            #     rows = cursor.fetchall()
            #     ...
        except Exception as e:
            error = str(e)
    return render(request, "demoapp/search_safe.html", {"query": query, "results": results, "error": error})
