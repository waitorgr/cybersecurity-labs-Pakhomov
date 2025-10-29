from django.urls import path
from . import views

app_name = 'email_crypto'

urlpatterns = [
    path('compose/', views.compose, name='compose'),
    path('outbox/', views.outbox, name='outbox'),
    path('message/<int:pk>/', views.detail, name='detail'),
    path('message/<int:pk>/download/', views.download_attachment, name='download_attachment'),
]
