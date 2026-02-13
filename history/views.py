from django.shortcuts import render
from dashboard.utils import dashboard_login_required, get_common_context

# Create your views here.

@dashboard_login_required
def history(request):
    user = request.user_obj
    context = get_common_context(request,user)
    if user.user_type == 'pharmacy':
        return render(request, 'pharmacy/history.html', context)
    elif user.user_type == 'lab':
        return render(request, 'lab/history.html', context)
    elif user.user_type == 'hospital':
        return render(request, 'hospital/history.html', context)
    elif user.user_type == 'doctor':
        return render(request, 'doctor/history.html', context)
    
    
@dashboard_login_required
def doctor_history_view(request):
    user = request.user_obj

    context = get_common_context(request, user)
    context["theme_colors"] = get_theme_colors("doctor")

    return render(
        request,
        "doctor/doctor_history.html",
        context
    )

@dashboard_login_required
def ajax_doctor_history(request):
    user = request.user_obj
    status = request.GET.get("status", "Accepted")
    page = request.GET.get("page", 1)

    qs = DoctorAppointment.objects.filter(
        doctor=user,
        status__iexact=status
    ).select_related(
        "user__userprofile",
        "address"
    ).order_by("-created_at")

    paginator = Paginator(qs, 5)
    page_obj = paginator.get_page(page)

    html = render_to_string(
        "partials/doctor_history_cards.html",
        {
            "appointments": page_obj,
            "page_obj": page_obj,
        },
        request=request
    )

    return JsonResponse({
        "html": html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages
    })
