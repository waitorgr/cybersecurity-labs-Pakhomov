from django.shortcuts import render
from .utils import check_personal_data, evaluate_strength, get_recommendations

def index(request):
    context = {}
    if request.method == "POST":
        name = request.POST.get("name", "")
        birth_date = request.POST.get("birth_date", "")
        password = request.POST.get("password", "")

        personal_data_matches = check_personal_data(password, name, birth_date)
        score = evaluate_strength(password)
        recommendations = get_recommendations(password, personal_data_matches, score)

        context = {
            "name": name,
            "birth_date": birth_date,
            "password": password,
            "score": score,
            "recommendations": recommendations,
        }

    return render(request, "index.html", context)