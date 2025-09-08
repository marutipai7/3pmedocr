from django.urls import path
from . import views

urlpatterns = [
    path('', views.shared, name='shared'),
    path("ocr/", views.ocr_upload, name="ocr_upload"),
]
