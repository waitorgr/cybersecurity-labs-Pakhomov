# urls.py
from django.urls import path
from .views import cipher_view, analyze_view

urlpatterns = [
    path('', cipher_view, name='cipher'),
    path('analyze/', analyze_view, name='cipher_analyze'),
]
