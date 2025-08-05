from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Sum, Count, DecimalField, Q
from django.utils import timezone
from .utils import dashboard_login_required
from .models import SettingMenu, CouponPerformance,  CalendarEvent
from registration.models import MedicalProviderProfile, NGOProfile, ClientProfile, AdvertiserProfile
from ngopost.models import NGOPost
from .models import TrendingCoupon
from points.models import PointsBadge, PointsHistory, PointsActionType
from django.shortcuts import render
from django.http import JsonResponse
import json
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.db.models.functions import TruncDate
import random
from datetime import date
from coupon.utils import get_saved_coupons_for_user
def get_common_context(request,user):
    user = request.user_obj
    user_type = user.user_type

    # Sidebar menu
    menu_items = SettingMenu.objects.filter(
        is_active=True, user_types__contains=[user_type]
    ).order_by('order')

    # Badge calculation
    if user_type == 'ngo':
        chart_action_types = ['Map', 'Referral', 'Post']
    elif user_type == 'client':
        chart_action_types = ['Map', 'Referral', 'Subscription']
    elif user_type == 'advertiser':
        chart_action_types = ['Map', 'Referral', 'Coupon']
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

    return {
        'user_profile': user,
        'sidebar_menu': menu_items,
        'badge': badge,
    }

@dashboard_login_required
def dashboard_home(request):
    user = request.user_obj
    user_type = user.user_type

    # Get sidebar menu
    menu_items = SettingMenu.objects.filter(
        is_active=True, user_types__contains=[user_type]
        ).order_by('order')
    # Get common context
    context = get_common_context(request, user)

    try:
        if user_type == 'ngo':
            ngo_profile = NGOProfile.objects.get(user=user)
            posts_qs = NGOPost.objects.filter(user=user)
            events = CalendarEvent.objects.filter(user=user,is_active=True)

            context.update({
                'ngo_profile': ngo_profile,
                'user_display_name': ngo_profile.ngo_name,
                'total_posts': posts_qs.count(),
                'total_views': posts_qs.aggregate(Sum('views'))['views__sum'] or 0,
                'total_target': posts_qs.aggregate(Sum('target_donation'))['target_donation__sum'] or 0,
                'total_received': posts_qs.aggregate(Sum('donation_received'))['donation_received__sum'] or 0,
                'trending_posts': posts_qs.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).order_by('-views')[:4],
                'events': events,
                'user': user,
            })
            return render(request, "dashboard/home_NGO.html", context)

        elif user_type == 'client':
            client_profile = ClientProfile.objects.get(user=user)
            context.update({
                'client_profile': client_profile,
                'user_display_name': client_profile.company_name,
                'user': user,
                # Add relevant client data if any, e.g. campaigns
            })
            return render(request, "dashboard/home.html", context)

        elif user_type == 'advertiser':
            advertiser_profile = AdvertiserProfile.objects.get(user=user)
            performance = CouponPerformance.objects.order_by('-date').first()
            trending_coupons = TrendingCoupon.objects.order_by('-created_at')[:5]
            performances = CouponPerformance.objects.order_by('date')[:8]
            events = CalendarEvent.objects.all().order_by('date')

            context.update({
                'advertiser_profile': advertiser_profile,
                'user_display_name': advertiser_profile.company_name,
                'performance': performance,
                'trending_coupons': trending_coupons,
                'events': events,
                'user': user,
            })

            print("DEBUG PERFORMANCE:", performance)
            return render(request, "dashboard/home_advertiser.html", context)

        elif user_type == 'provider':
            provider_profile = MedicalProviderProfile.objects.get(user=user)
            events = CalendarEvent.objects.all().order_by('date')
            
            context.update({
                'provider_profile': provider_profile,
                'user_display_name': provider_profile.company_name,
                'events': events,
                'user': user,
            })
            return render(request, "dashboard/home_provider.html", context)


    except Exception as e:
        # Log e if needed
        return render(request, "dashboard/not_found.html")
    
    
def get_coupon_chart_data(request):
    performances = CouponPerformance.objects.order_by('-date')[:8][::-1]  # last 8 entries, ascending

    data = {
        'labels': [perf.date.strftime('%d %b') for perf in performances],  # e.g., "17 Jul"
        'total_coupons': [perf.total_coupons for perf in performances],
        'total_redemptions': [perf.total_redemptions for perf in performances],
        'active_coupons': [perf.active_coupons for perf in performances],
    }
    return JsonResponse(data)

@csrf_exempt
@dashboard_login_required
def save_event(request):
    user = request.user_obj
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            date = data.get('date')
            time = data.get('time')

            # Get all future events for this user to avoid color conflicts
            event_date = datetime.strptime(date, '%Y-%m-%d').date()
            future_events = CalendarEvent.objects.filter(
                user=user,
                date__gte=event_date,
                is_active=True
            ).exclude(id=None)  # Exclude current event if it exists
            
            # Get colors already used for future events
            used_colors = set(future_events.values_list('color', flat=True))
            
            # Available colors (only dark, visible colors)
            all_colors = [
                'bg-slate-blue', 'bg-strong-red', 'bg-green', 'bg-vivid-orange',
                'bg-purple', 'bg-pink', 'bg-teal', 'bg-dark-blue', 'bg-dark-green', 'bg-dark-purple'
            ]
            
            # Filter out used colors
            available_colors = [color for color in all_colors if color not in used_colors]
            
            # If no colors available, use any color (fallback)
            if not available_colors:
                available_colors = all_colors
            
            random_color = random.choice(available_colors)

            if name and date and time:
                CalendarEvent.objects.create(
                    user=user,
                    name=name,
                    date=datetime.strptime(date, '%Y-%m-%d').date(),
                    time=datetime.strptime(time, '%H:%M').time(),
                    color=random_color
                )
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Missing fields'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@require_GET
@dashboard_login_required
def get_events(request):
    user = request.user_obj
    if request.method == 'GET':
        events = CalendarEvent.objects.filter(user=user)
        event_data = {}
        for event in events:
            date_str = event.date.strftime('%Y-%m-%d')
            if date_str not in event_data:
                event_data[date_str] = []
            event_data[date_str].append({
                'name': event.name,
                'time': event.time.strftime('%H:%M'),
                'color': event.color
            })

        return JsonResponse({'events': event_data})

@require_GET
@dashboard_login_required
def get_upcoming_events(request):
    user = request.user_obj
    if request.method == 'GET':
        # Get next 5 upcoming events for the user, ordered by date and time
        upcoming_events = CalendarEvent.objects.filter(
            user=user,
            date__gte=datetime.now().date(),
            is_active=True
        ).order_by('date', 'time')[:5]
        
        events_data = []
        for event in upcoming_events:
            event_data = {
                'name': event.name,
                'date': event.date.strftime('%Y-%m-%d'),
                'time': event.time.strftime('%H:%M'),
                'color': event.color,
                'color_hex': event.get_color_hex()
            }
            events_data.append(event_data)

        response_data = {'upcoming_events': events_data}
        return JsonResponse(response_data)

def logout_view(request):
    request.session.flush() 
    return redirect('/') 


@dashboard_login_required
def saved(request):
    user = request.user_obj
    context = get_common_context(request, user)
    if user.user_type == 'ngo':
    # Search query (optional)
        query = request.GET.get('query', '').strip().lower()

        # Menu items for sidebar
        menu_items = SettingMenu.objects.filter(
            is_active=True, user_types__contains=[user.user_type]
        ).order_by('order')

        try:
            ngo_profile = NGOProfile.objects.get(user=user)
            user_profile = user
        except NGOProfile.DoesNotExist:
            return render(request, "dashboard/not_found.html")

        # Get the limit parameter from the request, default to 50
        limit = request.GET.get('limit', '50')
        try:
            limit = int(limit)
        except ValueError:
            limit = 50

        # Base saved posts query
        saved_posts = NGOPost.objects.filter(user=user, saved=True)

        # Filter by query (if provided)
        if query:
            saved_posts = saved_posts.filter(
                Q(post_type__icontains=query) |
                Q(status__icontains=query) |
                Q(created_at__icontains=query)
            )

        # Apply limit
        saved_posts = saved_posts[:limit]

        context.update({
            'ngo_profile': ngo_profile,
            'user_profile': user_profile,
            'menu_items': menu_items,
            'saved_posts': saved_posts,
            'query': query,  # To retain search input
            'limit': str(limit),  # To retain limit select
        })

        return render(request, "dashboard/saved_ngo.html", context)
    
    elif user.user_type == 'advertiser':
        query = request.GET.get('query', '').strip()
        limit = request.GET.get('limit', '50')
        try:
            limit = int(limit)
        except ValueError:
            limit = 50

        saved_coupons = get_saved_coupons_for_user(user, query=query, limit=limit)
        print(f"Saved coupons count: {len(saved_coupons)}")
        print(f"Query: {query}")
        print(f"Limit: {limit}")

        context.update({
            'saved_coupon_history': saved_coupons,
            'query': query,
            'limit': str(limit),
            'today': timezone.now().date(),  # Add today's date for status comparison
        })

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # AJAX request: return only the coupon table HTML
            html = render_to_string("advertiser/partials/saved-coupon-history-table.html", context, request=request)
            return JsonResponse({"html": html})

        # Normal page render
        return render(request, "dashboard/saved_advertiser.html", context)
    elif user.user_type == 'provider':
        return render(request, "dashboard/saved_provider.html", context)


# ngo graph 
@require_GET
@dashboard_login_required
def get_ngo_graph_data(request):
    user = request.user_obj
    # print("Request User ID:", user)
    today = timezone.now().date()

    # Parse date input
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else today - timedelta(days=6)
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else today
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    # Truncate to date and aggregate
    posts = (
        NGOPost.objects
        .annotate(date=TruncDate('created_at'))  # Only date, no time
        # .filter(date__range=(start_date, end_date))
        .filter(
            user_id=user,
            date__range=(start_date, end_date)
        )
        .values('date')
        .annotate(
            total_post=Count('id'),
            total_views=Sum('views'),
            target_donation=Sum('target_donation'),
            donation_received=Sum('donation_received')
        )
        .order_by('date')
    )

    # Prepare data dictionary
    data_by_date = {entry['date']: entry for entry in posts}

    labels = []
    total_post = []
    total_views = []
    target_donation = []
    donation_received = []

    # Fill values for each day (even if zero)
    current_date = start_date
    while current_date <= end_date:
        entry = data_by_date.get(current_date, {})
        labels.append(current_date.strftime('%d-%b'))  # Format: 29-Jul
        total_post.append(entry.get('total_post', 0))
        total_views.append(entry.get('total_views', 0) or 0)
        target_donation.append(entry.get('target_donation', 0) or 0)
        donation_received.append(entry.get('donation_received', 0) or 0)
        current_date += timedelta(days=1)

    return JsonResponse({
        'labels': labels,
        'datasets': {
            'Total Post': total_post,
            'Total Views': total_views,
            'Target Donation': target_donation,
            'Donation Received': donation_received,
        }
    })
    
    
def get_ngo_graph_data_old(request):
    today = timezone.now().date()

    # Simulated day-wise data for last 7 days
    labels = []
    total_post = []
    total_views = []
    target_donation = []
    donation_received = []

    for i in range(7):
        date = today - timezone.timedelta(days=6 - i)
        posts = NGOPost.objects.filter(created_at__date=date)

        labels.append(date.strftime('%d-%b'))

        total_post.append(posts.count())
        total_views.append(posts.aggregate(Sum('views'))['views__sum'] or 0)
        target_donation.append(posts.aggregate(Sum('target_donation'))['target_donation__sum'] or 0)
        donation_received.append(posts.aggregate(Sum('donation_received'))['donation_received__sum'] or 0)

    return JsonResponse({
        'labels': labels,
        'datasets': {
            'Total Post': total_post,
            'Total Views': total_views,
            'Target Donation': target_donation,
            'Donation Received': donation_received,
        }
    })

@dashboard_login_required
def advertiser_advance(request):
    user = request.user_obj
    context = {
        "user": user
    }
    return render(request, "dashboard/advertiser_advance.html", context)

@dashboard_login_required
def cart(request):
    user = request.user_obj
    context = {
        "user": user
    }
    return render(request, "dashboard/cart.html", context)