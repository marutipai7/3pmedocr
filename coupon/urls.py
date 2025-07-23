from django.urls import path
from . import views

urlpatterns = [
    path('', views.coupon_view, name='coupons'),
    path('coupon_detail/<int:coupon_id>/', views.coupon_detail, name='coupon_detail'),
    path('coupon-history/', views.get_coupon_history, name='coupon_history'),
    path('saved-coupons/', views.get_saved_coupon_history, name='saved_coupons'),
    path('platform-bill/<int:coupon_id>/', views.platform_bill, name='platform_bill'),
] 