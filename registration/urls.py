from django.urls import path
from . import views 


urlpatterns = [
    path('register', views.welcome, name='welcome'),
    path('register/<str:role>', views.register_by_role, name='register_by_role'),
    path('save/customer', views.save_user, name='save_user'),
    path('save/ngo', views.save_ngo, name='save_ngo'),
    path('login', views.login_page, name='login_page'),
    path('auth/login', views.login_auth, name='login_auth'),
    path('save/advertiser', views.save_advertiser, name='save_advertiser'),
    path('save/client', views.save_client, name='save_client'),
    path('save/medical_provider', views.save_medical_provider, name='save_medical_provider'),        
    path("otp/send", views.send_otp, name="send_otp"),
    path("otp/verify", views.verify_otp, name="verify_otp"),
]
