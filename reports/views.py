from django.shortcuts import render
from dashboard.utils import dashboard_login_required, get_common_context
# Create your views here.

@dashboard_login_required
def reports(request):
    user = request.user_obj
    context = get_common_context(request, user)
    return render(request, 'reports.html', context)