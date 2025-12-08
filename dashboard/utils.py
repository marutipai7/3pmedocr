from django.shortcuts import redirect
from functools import wraps
from registration.models import User
from points.models import PointsActionType, PointsHistory, PointsBadge
from .models import SettingMenu
from django.db.models import Sum, Q
from registration.models import AdvertiserProfile, ClientProfile, PharmacyProfile, NGOProfile
from settings.models import UserColorScheme
import logging
from django.http import JsonResponse
logger = logging.getLogger(__name__)

def dashboard_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('/login')
        # Optionally: attach the user object
        request.user_obj = User.objects.filter(id=user_id).first()
        if not request.user_obj:
            return redirect('/login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def get_common_context(request, user):
    user = request.user_obj
    user_type = user.user_type
    menu_items = SettingMenu.objects.filter(
        is_active=True, user_types__contains=[user_type]
    ).order_by("order")

    # Badge calculation
    if user_type == "ngo":
        chart_action_types = ["Map", "Referral", "Post"]
        user_profile = NGOProfile.objects.filter(user=user).first()
    elif user_type == "client":
        chart_action_types = ["Map", "Referral", "Subscription", "Donate"]
        user_profile = ClientProfile.objects.filter(user=user).first()
    elif user_type == "advertiser":
        chart_action_types = ["Map", "Referral", "Coupon", "Donate"]
        user_profile = AdvertiserProfile.objects.filter(user=user).first()
    elif user_type == "pharmacy":
        chart_action_types = ["Map", "Referral", "Share", "Donate"]
        user_profile = PharmacyProfile.objects.filter(user=user).first()
    else:
        chart_action_types = []
        user_profile = None

    all_actions = PointsActionType.objects.filter(action_type__in=chart_action_types)
    action_points = {
        action.action_type: PointsHistory.objects.filter(
            user_id=user.id, action_type=action
        ).aggregate(total=Sum("points"))["total"]
        or 0
        for action in all_actions
    }

    total_points = sum(action_points.values())
    badge = (
        PointsBadge.objects.filter(min_points__lte=total_points)
        .filter(Q(max_points__gte=total_points) | Q(max_points__isnull=True))
        .order_by("min_points")
        .first()
    )

    if user_type == "ngo":
        user_display_name = user_profile.ngo_name if user_profile else "Unknown"
    else:
        user_display_name = (
            user_profile.company_name if user_profile else "Unknown"
        )
    trophy = None
    if user_type == "ngo":
        trophy = "trophy-ngo.svg"
    elif user_type == "client":
        trophy = "trophy-client.svg"
    elif user_type == "advertiser":
        trophy = "trophy-advertiser.svg"
    elif user_type == "pharmacy":
        trophy = "trophy-pharmacy.svg"
    elif user_type == "lab":
        trophy = "trophy-hospital.svg"
    tab_class_map = {
    "advertiser": "tab-btn-advertiser",
    "client": "tab-btn-client",
    "pharmacy": "tab-btn-pharmacy",
    "ngo": "tab-btn-ngo",
    "lab": "tab-btn-hospital",
    }

    active_tab_class_map = {
        "advertiser": "active-tab-advertiser",
        "client": "active-tab-client",
        "pharmacy": "active-tab-pharmacy",
        "ngo": "active-tab-ngo",
        "lab": "active-tab-hospital",
    }
    context = {
        "user_profile": user,
        "sidebar_menu": menu_items,
        "badge": badge,
        "user": user,
        "user_display_name": user_display_name,
        "total_points": total_points,
        "action_points": action_points,
        "chart_action_types": chart_action_types,
        "trophy": trophy,
    }
    context["tab_class"] = tab_class_map.get(user_type)
    context["active_tab_class"] = active_tab_class_map.get(user_type)
    context.update(get_theme_colors(user_type))
    return context

def get_theme_colors(user_type: str) -> dict:
    try:
        color_scheme_obj = UserColorScheme.objects.get(user_type=user_type, is_active=True)
        return color_scheme_obj.color_data

    except Exception as e:
        logger.error(f"Error fetching color scheme for user type '{user_type}': {e}")    
        return {}