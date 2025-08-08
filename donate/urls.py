from django.urls import path
from . import views

urlpatterns = [
    path('', views.donate_view, name='donate'),
    path('donate-pay/<int:post_id>/', views.donate_pay_view, name='donate-pay'),
    path('donation-history-ajax/', views.donation_history_ajax, name='donation-history-ajax'),
    path('export-donations-csv/', views.export_donations_csv, name='export-donations-csv'),
    path('get-donate-bill/<int:donation_id>/', views.get_donate_bill, name='get-donate-bill'),
    path('get-platform-bill/<int:donation_id>/', views.get_platform_bill, name='get-platform-bill'),
    path('toggle-saved/', views.toggle_saved_donation, name='toggle_saved_donation'),
] 