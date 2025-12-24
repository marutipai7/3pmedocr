# appointments/utils.py

from .models import (
    LabAppointments,
    DoctorAppointment,
    HospitalAppointments,
    AppointmentStatus,
    HospitalAppointmentStatus,
)

def get_appointment_stats(user_type, user):
    stats = {
        "total": 0,
        "pending": 0,
        "cancelled": 0,
        "completed": 0,
        "accepted": 0,
        "accepted_appointed": 0,
    }

    if user_type == "lab":
        # Lab sees appointments where it is the ACCEPTED lab
        qs = LabAppointments.objects.filter(accepted_lab__user=user)

        stats["total"] = qs.count()
        stats["pending"] = qs.filter(status=AppointmentStatus.PENDING).count()
        stats["cancelled"] = qs.filter(status="Cancelled").count()
        stats["completed"] = qs.filter(status=AppointmentStatus.COMPLETED).count()
        stats["accepted"] = qs.filter(status=AppointmentStatus.ACCEPTED).count()

        # Accepted + having appointment date
        stats["accepted_appointed"] = qs.filter(
            status=AppointmentStatus.ACCEPTED,
            preferred_date_time__isnull=False
        ).count()

    elif user_type == "doctor":
        qs = DoctorAppointment.objects.filter(doctor__user=user)

        stats["total"] = qs.count()
        stats["pending"] = qs.filter(status="Pending").count()
        stats["cancelled"] = qs.filter(status="Cancelled").count()
        stats["completed"] = qs.filter(status="Completed").count()
        stats["accepted"] = qs.filter(status="Accepted").count()
        stats["accepted_appointed"] = qs.filter(
            status="Accepted",
            preferred_date_time__isnull=False
        ).count()

    elif user_type == "hospital":
        qs = HospitalAppointments.objects.filter(accepted_hospital__user=user)

        stats["total"] = qs.count()
        stats["pending"] = qs.filter(status=HospitalAppointmentStatus.PENDING).count()
        stats["cancelled"] = qs.filter(status="Cancelled").count()
        stats["completed"] = qs.filter(status=HospitalAppointmentStatus.COMPLETED).count()
        stats["accepted"] = qs.filter(status=HospitalAppointmentStatus.ACCEPTED).count()
        stats["accepted_appointed"] = qs.filter(
            status=HospitalAppointmentStatus.ACCEPTED,
            preferred_date_from__isnull=False
        ).count()

    return stats
