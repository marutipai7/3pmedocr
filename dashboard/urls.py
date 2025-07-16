from django.urls import path
from .views import dashboard_home, logout_view, saved
from .views import get_coupon_chart_data

urlpatterns = [
    path('advertiser/', dashboard_home, name='advertiser-home'),
    path('api/coupon-chart-data/', get_coupon_chart_data, name='coupon_chart_data'),

]
