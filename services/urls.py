from django.urls import path
from . import views

urlpatterns = [
    path('', views.services, name='services'),

    # LAB
    path('add-services', views.save_lab_services, name='add_services'),
    path('get-services/', views.get_lab_services, name='get_lab_services'),

    # DOCTOR
    path('services/add-doctor-services/', views.save_doctor_services, name='save_doctor_services'),

    # # PHARMACY
    # path('pharmacy/services/save/', views.save_pharmacy_medicines, name='save_pharmacy_medicines'),

    # # 🔥 THIS WAS MISSING
    path('pharmacy/dropdowns/', views.pharmacy_dropdowns, name='pharmacy_dropdowns'),
]
