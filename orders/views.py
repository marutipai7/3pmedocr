from django.shortcuts import render
from dashboard.utils import dashboard_login_required
# Create your views here.

@dashboard_login_required
def orders(request):
    return render(request, 'orders.html')