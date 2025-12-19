from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Prefetch, Q
from dashboard.models import SettingMenu
from dashboard.utils import dashboard_login_required, get_common_context, get_theme_colors
from .models import LabAppointments, AppointmentStatus, LabAutoBidSettings, LabBidStatus, LabBidding, LabSubscription

@dashboard_login_required
def appointment_view(request):
    user = request.user_obj
    user_type = user.user_type

    menu_items = SettingMenu.objects.filter(
    is_active=True, user_types__contains=[user_type]
    ).order_by('order')

    active_status = [
        AppointmentStatus.PENDING,
        AppointmentStatus.ACCEPTED,
        AppointmentStatus.COMPLETED
    ]

    active_appointments = LabAppointments.objects.select_related(
        "test_package","test_type", "test_description"
    ).filter(
        status__in=active_status
    ).order_by('-created_at')

    context = get_common_context(request, user)
    context["theme_colors"] = get_theme_colors(user_type)
    context["sidebar_menu"] = menu_items
    context["appointments"] = active_appointments
    
    print("Acive Appointments:", active_appointments[0] if active_appointments else "No Appointments")
    if user_type == "lab":
        return render(request, 'lab/lab_appointment.html', context)
    elif user_type == "doctor":
        return render(request, 'doctor/doctor_appointment.html', context)
    else:
        return render(request, 'appointments.html', context)
