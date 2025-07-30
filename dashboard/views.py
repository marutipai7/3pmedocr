from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Sum, Count, DecimalField
from django.utils import timezone
from .utils import dashboard_login_required
from .models import SettingMenu, CouponPerformance,  CalendarEvent
from registration.models import NGOProfile, ClientProfile, AdvertiserProfile
from ngopost.models import NGOPost
from django.db.models import Q
from .models import TrendingCoupon
from django.shortcuts import render
from django.http import JsonResponse
import json
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.db.models.functions import TruncDate

@dashboard_login_required
def dashboard_home(request):
    user = request.user_obj
    user_type = user.user_type

    # Get sidebar menu
    menu_items = SettingMenu.objects.filter(
        is_active=True, user_types__contains=[user_type]
        ).order_by('order')

    context = {
        'user_profile': user,
        'menu_items': menu_items,
    }

    try:
        if user_type == 'ngo':
            ngo_profile = NGOProfile.objects.get(user=user)
            posts_qs = NGOPost.objects.filter(user=user)

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
            })
            return render(request, "dashboard/home_NGO.html", context)

        elif user_type == 'client':
            client_profile = ClientProfile.objects.get(user=user)
            context.update({
                'client_profile': client_profile,
                'user_display_name': client_profile.company_name,
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
                
            })

            print("DEBUG PERFORMANCE:", performance)
            return render(request, "dashboard/home_advertiser.html", context)




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

# @csrf_exempt
def save_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            date = data.get('date')
            time = data.get('time')

            if name and date and time:
                CalendarEvent.objects.create(
                    name=name,
                    date=datetime.strptime(date, '%Y-%m-%d').date(),
                    time=datetime.strptime(time, '%H:%M').time()
                )
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Missing fields'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_events(request):
    if request.method == 'GET':
        events = CalendarEvent.objects.all()
        event_data = {}
        for event in events:
            date_str = event.date.strftime('%Y-%m-%d')
            if date_str not in event_data:
                event_data[date_str] = []
            event_data[date_str].append({
                'name': event.name,
                'time': event.time.strftime('%H:%M')
            })

        return JsonResponse({'events': event_data})


def logout_view(request):
    request.session.flush() 
    return redirect('/') 


@dashboard_login_required
def saved(request):
    user = request.user_obj
    
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

    context = {
        'ngo_profile': ngo_profile,
        'user_profile': user_profile,
        'menu_items': menu_items,
        'saved_posts': saved_posts,
        'query': query,  # To retain search input
        'limit': str(limit),  # To retain limit select
    }

    return render(request, "dashboard/saved.html", context)

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
    