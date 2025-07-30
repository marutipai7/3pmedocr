from django.urls import path
from .views import dashboard_home, logout_view, saved
from .views import get_coupon_chart_data
from .views import save_event, get_events
from . import views




urlpatterns = [
    path('advertiser/', dashboard_home, name='advertiser-home'),
    path('api/coupon-chart-data/', get_coupon_chart_data, name='coupon_chart_data'),
    path('save-event/', views.save_event, name='save_event'),
    path('get-events/', get_events, name='get_events'),
    path('ngo-graph-data/', views.get_ngo_graph_data, name='ngo-graph-data'),
]
