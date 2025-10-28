from django.urls import path
from .views import index, verify_view, download_signed_document

urlpatterns = [
    path('', index, name='index'),
    path('verify/', verify_view, name='verify'),
    path('download/', download_signed_document, name='download_signed_document'),
]
