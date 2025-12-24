from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Prefetch, Q
from dashboard.models import SettingMenu
from dashboard.utils import dashboard_login_required, get_common_context, get_theme_colors
from .models import (
    DoctorAppointment,
    LabAppointments, 
    HospitalAppointments, 
    AppointmentStatus, 
    HospitalAppointmentStatus, 
    LabTestPackages, 
    LabTestType, 
    LabTestDescription, 
    HealthIssue,
    SpecializationServiceMap,
    HealthIssueServiceMap, 
    HospitalBedRoom, 
    HospitalCategory, 
    HospitalServiceDescription, 
    HospitalServiceType,
    )
from appointments.utils import get_appointment_stats

@dashboard_login_required
def appointment_view(request):
    user = request.user_obj
    user_type = user.user_type

    menu_items = SettingMenu.objects.filter(
        is_active=True,
        user_types__contains=[user_type]
    ).order_by("order")

    context = get_common_context(request, user)
    context["theme_colors"] = get_theme_colors(user_type)
    context["sidebar_menu"] = menu_items
    
    stats = get_appointment_stats(user_type, user)

    print("📊 Appointment Stats:", stats)

    context.update({
        "total_appointments": stats.get("total", 0),
        "pending_appointments": stats.get("pending", 0),
        "cancelled_appointments": stats.get("cancelled", 0),
        "completed_appointments": stats.get("completed", 0),
        "accepted_appointments": stats.get("accepted", 0),
        "accepted_appointed_appointments": stats.get("accepted_appointed", 0),
    })

    if user_type == "lab":
        appointments = LabAppointments.objects.select_related(
            "user__userprofile",
            "test_package",
            "test_type",
            "test_description",
            "address",
            "user",
        ).order_by("-created_at")

        template = "lab/lab_appointment.html"

    elif user_type == "doctor":
        appointments = DoctorAppointment.objects.select_related(
            "user__userprofile",
            "address",
            "user",
            "doctor",
        ).order_by("-created_at")

        template = "doctor/doctor_appointment.html"

    elif user_type == "hospital":
        appointments = HospitalAppointments.objects.select_related(
            "user__userprofile",
            "service_type",
            "description",
            "category",
            "bed_room",
            "address",
            "user",
        ).order_by("-created_at")

        template = "hospital/hospital_appointment.html"

    else:
        appointments = []
        template = "dashboard/no_access.html"

    context["appointments"] = appointments

    return render(request, template, context)

@dashboard_login_required
def list_avaibale_appointments(request):
    user = request.user_obj
    user_type = user.user_type

    menu_items = SettingMenu.objects.filter(
        is_active=True,
        user_types__contains=[user_type]
    ).order_by("order")

    context = get_common_context(request, user)
    context["theme_colors"] = get_theme_colors(user_type)
    context["sidebar_menu"] = menu_items
    stats = get_appointment_stats(user_type, user)

    print("📊 Available Appointment Stats:", stats)

    context.update({
        "total_appointments": stats.get("total", 0),
        "pending_appointments": stats.get("pending", 0),
        "cancelled_appointments": stats.get("cancelled", 0),
        "completed_appointments": stats.get("completed", 0),
        "accepted_appointments": stats.get("accepted", 0),
        "accepted_appointed_appointments": stats.get("accepted_appointed", 0),
    })

    if user_type == "lab":
        appointments = LabAppointments.objects.select_related(
            "user__userprofile",
            "test_package",
            "test_type",
            "test_description",
            "address",
            "user",
        ).filter(
            status=AppointmentStatus.PENDING
        ).order_by("-created_at")

        template = "lab/lab_appointment.html"

    elif user_type == "doctor":
        appointments = DoctorAppointment.objects.select_related(
            "user__userprofile",
            "address",
            "user",
        ).filter(
            status="Pending"
        ).order_by("-created_at")

        template = "doctor/doctor_appointment.html"

    elif user_type == "hospital":
        appointments = HospitalAppointments.objects.select_related(
            "user__userprofile",
            "service_type",
            "description",
            "category",
            "bed_room",
            "address",
            "user",
        ).filter(
            status=HospitalAppointmentStatus.PENDING
        ).order_by("-created_at")

        template = "hospital/hospital_appointment.html"

    else:
        appointments = []
        template = "dashboard/no_access.html"

    context["appointments"] = appointments

    return render(request, template, context)
