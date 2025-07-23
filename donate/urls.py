from django.urls import path
from . import views

urlpatterns = [
    path('', views.donate_view, name='donate'),
    path('donate-pay/<int:post_id>/', views.donate_pay_view, name='donate-pay'),
    path('donation-history-ajax/', views.donation_history_ajax, name='donation-history-ajax'),
    path('export-donations-csv/', views.export_donations_csv, name='export_donations_csv'),
] 