from django.shortcuts import redirect
from functools import wraps
from registration.models import User
from points.models import PointsActionType, PointsHistory, PointsBadge
from .models import SettingMenu
from django.db.models import Sum, Q
from registration.models import AdvertiserProfile, ClientProfile, MedicalProviderProfile, NGOProfile
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

def get_common_context(request,user):
    user = request.user_obj
    user_type = user.user_type
    menu_items = SettingMenu.objects.filter(
        is_active=True, user_types__contains=[user_type]
    ).order_by('order')

    # Badge calculation
    if user_type == 'ngo':
        chart_action_types = ['Map', 'Referral', 'Post']
        user_profile = NGOProfile.objects.filter(user=user).first()
    elif user_type == 'client':
        chart_action_types = ['Map', 'Referral', 'Subscription', 'Donation']
        user_profile = ClientProfile.objects.filter(user=user).first()
    elif user_type == 'advertiser':
        chart_action_types = ['Map', 'Referral', 'Coupon', 'Donation']
        user_profile = AdvertiserProfile.objects.filter(user=user).first()
    elif user_type == 'provider':
        chart_action_types = ['Map', 'Referral', 'Coupon', 'Donation']
        user_profile = MedicalProviderProfile.objects.filter(user=user).first()
    else:
        chart_action_types = []

    all_actions = PointsActionType.objects.filter(action_type__in=chart_action_types)
    action_points = {
        action.action_type: PointsHistory.objects.filter(
            user_id=user.id, action_type=action
        ).aggregate(total=Sum('points'))['total'] or 0
        for action in all_actions
    }

    total_points = sum(action_points.values())
    badge = PointsBadge.objects.filter(
        min_points__lte=total_points
    ).filter(
        Q(max_points__gte=total_points) | Q(max_points__isnull=True)
    ).order_by('min_points').first()

    if user_type == 'ngo':
        user_display_name = user_profile.ngo_name
    else:
        user_display_name = user_profile.company_name
    context = {
        'user_profile': user,
        'sidebar_menu': menu_items,
        'badge': badge,
        'user': user,
        'user_display_name': user_display_name,
    }
    context.update(handle_theme_context(user_type))
    return context

def handle_theme_context(user_type):
    try:
        color_scheme_obj = UserColorScheme.objects.get(user_type=user_type, is_active=True)
        return color_scheme_obj.color_data

    except Exception as e:
        logger.error(f"Error fetching color scheme for user type '{user_type}': {e}")    
        return {}

# def get_theme_colors(user_type: str) -> dict:
#     """
#     Fetch active theme colors for the given user_type.
#     Falls back to 'user' type if no match is found.
#     Returns a dict with '_' instead of '-' in keys.
#     """
#     def normalize_keys(color_data: dict) -> dict:
#         return {k.replace("-", "_"): v for k, v in color_data.items()}

#     try:
#         color_scheme_obj = UserColorScheme.objects.get(user_type=user_type, is_active=True)
#         colors = normalize_keys(color_scheme_obj.color_data)
#         logger.info(f"[Theme Colors] Found active scheme for '{user_type}': {colors}")
#         return colors
#     except UserColorScheme.DoesNotExist:
#         logger.warning(f"[Theme Colors] No active scheme found for '{user_type}', falling back to 'user'")
#         try:
#             default_scheme = UserColorScheme.objects.get(user_type='user', is_active=True)
#             colors = normalize_keys(default_scheme.color_data)
#             logger.info(f"[Theme Colors] Using fallback 'user' scheme: {colors}")
#             return colors
#         except UserColorScheme.DoesNotExist:
#             logger.error("[Theme Colors] No active color scheme found for user or default")
#             return {}