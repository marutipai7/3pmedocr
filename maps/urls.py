from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map_view'),
    path('get_routes/', views.get_routes, name='get_routes'),
    path('get_places/', views.get_amenities, name='get_places'),
    path('search/', views.search_by_name, name='search_by_name'),
    path('save_location/', views.saved_amenity, name='save_location'),
    path('search_history/', views.search_history, name='search_history'),
    path('remove_saved_location/', views.remove_from_saved, name='remove_saved_location'),
    path('remove_search_history/', views.remove_from_history, name='get_saved_locations'),
]
