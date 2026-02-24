from django.shortcuts import render
from dashboard.utils import dashboard_login_required, get_common_context
# Create your views here.

@dashboard_login_required
def staffs(request):
    user = request.user_obj
    context = get_common_context(request,user)
    if user.user_type == "lab":
        return render(request, 'lab/technicians.html', context)
    elif user.user_type == "hospital":
        return render(request, 'hospital/doctors.html', context)