from django.urls import path
from . import views

urlpatterns = [
    path('', views.services, name='reports'),
    path('add-services', views.save_lab_services, name='add_services'),
    path("get-services/", views.get_lab_services, name="get_lab_services"),

]
