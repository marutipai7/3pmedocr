from django.urls import path
from . import views


app_name = 'points'

urlpatterns = [
    path('', views.points_dashboard, name='points'),
    path('get-cards/', views.get_coupon_cards, name='get_cards'),
    path('history/', views.points_history_view, name='points_history'),
    path('history/ajax/', views.ajax_filtered_points, name='ajax_filtered_history'),

] 