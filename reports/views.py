from django.shortcuts import render
from dashboard.utils import dashboard_login_required, get_common_context
# Create your views here.

@dashboard_login_required
def reports(request):
    user = request.user_obj
    context = get_common_context(request, user)
    if user.user_type == 'pharmacy':
        return render(request, 'pharmacy_reports.html', context)
    elif user.user_type == 'lab':
        return render(request, 'lab_reports.html', context)
    elif user.user_type == 'doctor':
        return render(request, 'doctor_reports.html', context)
    elif user.user_type == 'hospital':
        return render(request, 'hospital_reports.html', context)
    else:
        return render(request, 'reports.html', context)