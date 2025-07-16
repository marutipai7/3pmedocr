from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_view, name='posts'),
    path('post_save/', views.save_ngo_post, name='save_ngo_post'),
    path('<int:post_id>/detail/', views.post_detail, name='post_detail'),
    path('toggle-saved/', views.toggle_saved_post, name='toggle_saved_post'),
    path('update-status/', views.update_post_status, name='update_post_status'),
    path('ajax/post-history/', views.post_history_ajax, name='post_history_ajax'),
]   