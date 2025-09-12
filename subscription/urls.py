from django.urls import path
from . import views

urlpatterns = [
    path('', views.subscription_view, name='subscription'),
    path('calculate-price/', views.calculate_price, name='calculate_price'),
    path('subscribe/', views.subscribe_plan, name='subscribe_plan'),
    path("subscription-history/", views.subscription_history, name="subscription_history"),
    path('current-summary/', views.current_subscription_summary, name='current_subscription'),
    path('invoice/<int:history_id>/', views.subscription_invoice, name='subscription_invoice'),
    path("subscription-history/<int:history_id>/bookmark/", views.toggle_subscription_bookmark, name="toggle_subscription_bookmark"),
]
