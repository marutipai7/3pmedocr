from appointments import views
from django.urls import path

urlpatterns = [
    path('', views.appointment_view, name='appointment'),
    path('all-appointments/', views.list_avaibale_appointments, name='all-appointments'),
]