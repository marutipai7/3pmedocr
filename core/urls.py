from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from registration import views
from dashboard import views as dashboard_views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('admin/', admin.site.urls),
    path('user/', include('registration.urls')),
    path('dashboard', dashboard_views.dashboard_home, name='dashboard'),
    path('dashboard/saved', dashboard_views.saved, name='saved'),
    path('logout', dashboard_views.logout_view, name='logout'),
    path('map/', include('maps.urls')),
    path('help/', include('support.urls')),
    path('settings/', include('settings.urls')),
    path('posts/', include('ngopost.urls')),
    path('donate/', include('donate.urls')),
    path('post/toggle-save', dashboard_views.toggle_saved_post, name='dashboard_toggle_save'),
    path('post/update-status', dashboard_views.update_post_status, name='dashboard_update_status'),
    # ... other apps
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # ... existing code ...
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)