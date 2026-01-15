from django.shortcuts import render
from dashboard.utils import dashboard_login_required, get_common_context

# Create your views here.

@dashboard_login_required
def history(request):
    user = request.user_obj
    context = get_common_context(request,user)
    if user.user_type == 'pharmacy':
        return render(request, 'pharmacy/history.html', context)
    return render(request, 'history.html', context)