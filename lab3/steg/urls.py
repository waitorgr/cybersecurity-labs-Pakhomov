from django.urls import path
from . import views

app_name = 'steg'
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.hide_view, name='hide'),
    path('extract/', views.extract_view, name='extract'),
]