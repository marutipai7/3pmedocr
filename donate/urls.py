from django.urls import path
from . import views

urlpatterns = [
    path('', views.donate_view, name='donate'),
    path('donate-pay/<int:post_id>/', views.donate_pay_view, name='donate-pay'),
    path('donation-history/', views.get_donation_history, name='donation-history-ajax'),
    path('export-donation-history/', views.export_donation_history, name='export-donation-history'),
    path('get-donate-bill/<int:donation_id>/', views.get_donate_bill, name='get-donate-bill'),
    path('get-platform-bill/<int:donation_id>/', views.get_platform_bill, name='get-platform-bill'),
    path('toggle-saved/', views.toggle_saved_donation, name='toggle_saved_donation'),
    path('get-organization-posts/', views.get_organization_posts, name='get-organization-posts'),
    ] 