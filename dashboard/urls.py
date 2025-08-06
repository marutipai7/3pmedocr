from django.urls import path
from . import views

urlpatterns = [
    path('advertiser/', views.dashboard_home, name='advertiser-home'),
    path('api/coupon-chart-data/', views.get_coupon_chart_data, name='coupon_chart_data'),
    path('save-event/', views.save_event, name='save_event'),
    path('get-events/', views.get_events, name='get_events'),
    path('get-upcoming-events/', views.get_upcoming_events, name='get_upcoming_events'),
    path('ngo-graph-data/', views.get_ngo_graph_data, name='ngo-graph-data'),
    path('saved/', views.saved, name='saved'),
    path('advance/', views.advertiser_advance, name='advertiser-advance'),
    path('cart/', views.cart, name='cart'),
    path('saved-coupon-history/', views.adv_saved_coupon_history, name='saved_coupon_history'),
    path('coupon_detail/<int:coupon_id>/', views.coupon_detail, name='coupon_detail'),
    path('saved/platform-bill/<int:coupon_id>/', views.platform_bill, name='platform_bill'),
    path('export-saved-coupon-history/', views.export_saved_coupon_history, name='export_saved_coupon_history'),
]
