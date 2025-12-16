from django.urls import path
from . import views

urlpatterns = [
    ## settings
    path('', views.settings_page, name='settings_page'),
    path('update-ngo-profile/', views.update_ngo_profile, name='update_ngo_profile'),
    path('update-advertiser-profile/', views.update_advertiser_profile, name='update_advertiser_profile'),
    path('update_client-profile/', views.update_client_profile, name='update_client_profile'),
    path('update-pharmacy-profile/', views.update_pharmacy_profile, name='update_pharmacy_profile'),
    path('update-lab-profile', views.update_lab_profile, name='update_lab_profile'),
    path('update-doctor-profile', views.update_doctor_profile, name='update_doctor_profile'),
    path('update-hospital-profile', views.update_hospital_profile, name='update_hospital_profile'),
    path('update-notification-field/', views.update_notification_field, name='update_notification_field'),
    path('update-document/', views.update_user_document, name='update_document'),
    path('clear-search-history/', views.clear_search_history, name='clear_search_history'),
    path('clear-saved-data/', views.clear_saved_data, name='clear_saved_data'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('change-password/', views.change_password, name='change_password'),
    # path('get_user_theme_api/', views.get_user_theme_api, name='get_user_theme_api'),
    # path('account-details/', views.get_account_details, name='account-details'),

    ## donate
    path('donate/', views.donate_view, name='donate'),
    path('donate-pay/<int:post_id>/', views.donate_pay_view, name='donate-pay'),
    path('donation-history/', views.get_donation_history, name='donation-history-ajax'),
    path('export-donation-history/', views.export_donation_history, name='export-donation-history'),
    path('get-donate-bill/<int:donation_id>/', views.get_donate_bill, name='get-donate-bill'),
    path('get-platform-bill/<int:donation_id>/', views.get_platform_bill, name='get-platform-bill'),
    path('toggle-saved/', views.toggle_saved_donation, name='toggle_saved_donation'),
    path('get-organization-posts/', views.get_organization_posts, name='get-organization-posts'),

    ## rewards
    path('rewards/', views.points_dashboard, name='points'),
    path('get-cards/', views.get_coupon_cards, name='get_cards'),
    path('get-popular-coupons/', views.get_popular_coupon_cards, name='get_popular_coupon_cards'),
    path('history/', views.points_history_view, name='points_history'),
    path('history/ajax/', views.ajax_filtered_points, name='ajax_filtered_history'),
    path('claim-coupon/', views.claim_coupon, name='claim-coupon'),
    path("claimed-coupons/ajax/", views.get_claimed_coupons, name="get_claimed_coupons"),

    ## support
    path('support/', views.support_view, name='support_view'),
    path('submit-ticket/', views.submit_support_ticket, name='submit_support_ticket'),
    path('filter-tickets/', views.filter_support_tickets, name='filter_support_tickets'),
    path('get-bot-content/', views.get_bot_content_api, name='get_bot_content_api'),
    path('get-user-tickets/', views.get_user_tickets, name='get_user_tickets'),
    path('get-issue-options/', views.get_issue_options, name='get-issue-options'),
    path('get-tickets-list/', views.get_ticket_lists, name='get-tickets-list'),
    path('get-tickets-details/', views.ticket_details, name='get-tickets-details'),
    path('get-tickets-filters/', views.filter_tickets, name='get-tickets-filters'),
    path('get-faq-lists/', views.faq_lists, name='get-faq-lists'),
    path('send-support-email/', views.send_support_email, name='send-support-email'),
]
