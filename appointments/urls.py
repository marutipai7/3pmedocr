from appointments import views
from django.urls import path

urlpatterns = [
    path('', views.appointment_view, name='appointment'),
]