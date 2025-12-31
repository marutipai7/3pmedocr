from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from dashboard.models import SettingMenu
from dashboard.utils import dashboard_login_required, get_common_context, get_theme_colors

from .models import (
    DoctorAppointment,
    LabAppointments,
    HospitalAppointments,
    AppointmentStatus,
    HospitalAppointmentStatus,
)

from appointments.utils import get_appointment_stats


# -------------------------------
# STATUS MAPS (IMPORTANT)
# -------------------------------

HOSPITAL_STATUS_MAP = {
    "pending": HospitalAppointmentStatus.PENDING,
    "accepted": HospitalAppointmentStatus.ACCEPTED,
    "completed": HospitalAppointmentStatus.COMPLETED,
    "cancelled": HospitalAppointmentStatus.CANCELLED,
    # NOTE: missed is NOT stored yet
}

LAB_DOCTOR_STATUS_MAP = {
    "pending": "Pending",
    "accepted": "Accepted",
    "completed": "Completed",
    "cancelled": "Cancelled",   # ✅ correct spelling
    "canceled": "Cancelled",    # ✅ map US → UK
    "missed": None,             # ❌ not stored yet
}


# -------------------------------
# MAIN APPOINTMENT PAGE
# -------------------------------

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

    # Initial page load (AJAX will override content)
    if user_type == "lab":
        template = "lab/lab_appointment.html"
    elif user_type == "doctor":
        template = "doctor/doctor_appointment.html"
    elif user_type == "hospital":
        template = "hospital/hospital_appointment.html"
    else:
        template = "dashboard/layout.html"

    return render(request, template, context)


# -------------------------------
# AJAX APPOINTMENTS ENDPOINT
# -------------------------------

@dashboard_login_required
def ajax_appointments(request):
    user = request.user_obj
    user_type = user.user_type
    status = request.GET.get("status", "all")

    # ---------------- LAB ----------------
    if user_type == "lab":
        qs = LabAppointments.objects.select_related(
            "user__userprofile",
            "test_package",
            "test_type",
            "test_description",
            "address",
            "user",
        )

        if status != "all":
            mapped_status = LAB_DOCTOR_STATUS_MAP.get(status)
            if mapped_status:
                qs = qs.filter(status=mapped_status)
            else:
                qs = qs.none()   # missed → empty safely


    # ---------------- DOCTOR ----------------
    elif user_type == "doctor":
        qs = DoctorAppointment.objects.select_related(
            "user__userprofile",
            "address",
            "user",
        )

        if status != "all":
            mapped_status = LAB_DOCTOR_STATUS_MAP.get(status)
            if mapped_status:
                qs = qs.filter(status=mapped_status)
            else:
                qs = qs.none()


    # ---------------- HOSPITAL ----------------
    elif user_type == "hospital":
        qs = HospitalAppointments.objects.select_related(
            "user__userprofile",
            "service_type",
            "description",
            "category",
            "bed_room",
            "address",
            "user",
        )

        if status == "missed":
            qs = qs.none()  # not implemented yet

        elif status != "all":
            mapped_status = HOSPITAL_STATUS_MAP.get(status)
            if mapped_status:
                qs = qs.filter(status=mapped_status)
            else:
                qs = qs.none()

    else:
        qs = HospitalAppointments.objects.none()

    qs = qs.order_by("-created_at")

    html = render_to_string(
        "partials/appointment-cards-list.html",
        {"appointments": qs},
        request=request
    )

    return JsonResponse({"html": html})

