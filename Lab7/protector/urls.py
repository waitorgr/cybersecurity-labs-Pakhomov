from django.urls import path
from . import views

app_name = 'protector'

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('status/<int:pk>/', views.status_view, name='status'),
    path('encrypt/<int:pk>/', views.encrypt_data_view, name='encrypt_data'),
    path('decrypt/', views.decrypt_data_view, name='decrypt_data'),
]
