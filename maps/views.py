from django.shortcuts import render, redirect
from dashboard.utils import dashboard_login_required

@dashboard_login_required
def map_view(request):
    return render(request, 'maps/maps.html')