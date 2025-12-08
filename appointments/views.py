from django.shortcuts import render
from dashboard.models import SettingMenu
from dashboard.utils import dashboard_login_required, get_common_context, get_theme_colors


@dashboard_login_required
def appointment_view(request):
    user = request.user_obj
    user_type = user.user_type
    menu_items = SettingMenu.objects.filter(
    is_active=True, user_types__contains=[user_type]
    ).order_by('order')
    context = get_common_context(request, user)
    context["theme_colors"] = get_theme_colors(user_type)
    context["sidebar_menu"] = menu_items
    pass
    return render(request, 'lab/lab_appointment.html', context)