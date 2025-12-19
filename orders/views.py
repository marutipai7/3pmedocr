from django.shortcuts import render
from dashboard.utils import dashboard_login_required, get_common_context

@dashboard_login_required
def orders(request):
    user = request.user_obj
    context = get_common_context(request, user)
    return render(request, 'orders.html', context)