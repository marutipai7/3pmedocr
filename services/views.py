from django.shortcuts import render
from django.http import HttpResponse
from dashboard.utils import dashboard_login_required, get_common_context
# Create your views here.

@dashboard_login_required
def services(request):
    user = request.user_obj
    context = get_common_context(request, user)
    if user.user_type == 'pharmacy':
        return render(request, 'pharmacy/services.html', context)
    elif user.user_type == 'lab':
        return render(request, 'lab/services.html', context)
    elif user.user_type == 'doctor':
        return render(request, 'doctor/services.html', context)
    elif user.user_type == 'hospital':
        return render(request, 'hospital/services.html', context)
