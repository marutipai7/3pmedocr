from django.urls import path
from . import views

urlpatterns = [
    path('', views.coupon_view, name='coupons'),
    path('coupon_detail/<int:coupon_id>/', views.coupon_detail, name='coupon_detail'),
    path('toggle-saved/', views.toggle_saved_coupon, name='toggle_saved_coupon'),
] 