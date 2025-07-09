from django.urls import path
from . import views

urlpatterns = [
    path('', views.donate_view, name='donate'),
    path('donate-pay/<int:post_id>/', views.donate_pay_view, name='donate-pay'),
] 