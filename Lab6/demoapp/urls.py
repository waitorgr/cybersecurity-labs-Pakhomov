from django.urls import path
from . import views

app_name = "demoapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("search/vulnerable/", views.search_vulnerable, name="search_vulnerable"),
    path("search/safe/", views.search_safe, name="search_safe"),
]
