from django.urls import path
from . import views

urlpatterns = [
    path('', views.history, name='reports'),
    path("doctor/history/ajax/", views.ajax_doctor_history, name="ajax_doctor_history"),
]
