from django.shortcuts import render
from dashboard.utils import dashboard_login_required
from .models import PointsHistory,PointsActionType,PointsBadge
from collections import defaultdict
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
import datetime
from django.db.models import Sum
from registration.models import User 
from django.db.models import Q



@dashboard_login_required
def points_dashboard(request):
    user = request.user_obj
    user_type = getattr(user, 'user_type', '').lower()

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
    user_points = total_points  # already calculated
    
    all_badges =PointsBadge.objects.all()
    badge = PointsBadge.objects.filter(
    min_points__lte=user_points
).filter(
    Q(max_points__gte=user_points) | Q(max_points__isnull=True)
).order_by('min_points').first()

    


    badge_name='';
    badge_image='';
    if badge:
        badge_name = badge.name
        badge_image = badge.image_url if badge_image else '/static/images/default-badge.svg'
        
    else:
        badge_name = "No Badge"
        badge_image = "/static/images/default-badge.svg"
    

    



    # 📊 Chart data (last 7 days)
    chart_data = defaultdict(lambda: [0] * 7)
    today = datetime.date.today()
    last_7_days = [today - datetime.timedelta(days=6 - i) for i in range(7)]

    for day_index, day in enumerate(last_7_days):
        for action_type in chart_action_types:
            action_obj = PointsActionType.objects.filter(action_type__iexact=action_type).first()
            if action_obj:
                points = PointsHistory.objects.filter(
                    user=user,
                    action_type=action_obj,
                    timestamp__date=day
                ).aggregate(total=Sum('points'))['total'] or 0
                chart_data[action_type.title()][day_index] = points

    chart_labels = [d.strftime('%d/%m') for d in last_7_days]

    # 🔍 Search & Filters
    search_query = request.GET.get('search', '').strip().lower()
    date_filter = request.GET.get('date_filter', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    history_queryset = PointsHistory.objects.filter(user=user).select_related('action_type')

    # Date Filter logic
    if date_filter == 'last_week':
        last_week = today - datetime.timedelta(days=7)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_week)
    elif date_filter == 'last_month':
        last_month = today - datetime.timedelta(days=30)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_month)
    elif date_filter == 'last_year':
        last_year = today - datetime.timedelta(days=365)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_year)
    elif date_filter == 'custom' and start_date and end_date:
        try:
            start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            history_queryset = history_queryset.filter(timestamp__date__range=(start_dt, end_dt))
        except ValueError:
            pass  # silently ignore invalid date input

    # Apply search filter after date filtering
    history_data = [
        {
            'timestamp': h.timestamp.strftime('%d/%m/%y, %H:%M'),
            'action_type': h.action_type.action_type.title() if h.action_type else 'Unknown',
            'points': h.points,
            'status': 'Completed'
        }
        for h in history_queryset.order_by('-timestamp')
    ]

    if search_query:
        history_data = [
            entry for entry in history_data
            if search_query in entry['action_type'].lower()
            or search_query in entry['timestamp'].lower()
            or search_query in entry['status'].lower()
        ]
    #print(chart_data)
    print(action_points)
    return render(request, 'ngo_points.html', {
        'total_points': total_points,
        'action_points': action_points,
        'chart_labels': chart_labels,
        'chart_data': dict(chart_data),
        'history': history_data,
        'all_badges': all_badges,
        'badge': badge,
    })

def get_coupon_cards(request):
    data = [
        {
            "title": "Wireless Bluetooth Headphones",
            "description": "High-quality over-ear headphones with noise cancellation.",
            "category": "Electronics",
            "code": "ELEC1001",
            "brand_name": "SoundMax"
        },
        {
            "title": "Organic Green Tea Bags",
            "description": "100 eco-friendly, antioxidant-rich green tea bags.",
            "category": "Groceries",
            "code": "GROC2021",
            "brand_name": "Nature's Bliss"
        }
    ]
    html = render_to_string("partials/coupon_cards.html", {"products": data})
    return JsonResponse({"html": html})


def points_history_view(request):
    history = filter_points(request)
    return render(request, 'partials/points_table.html', {'history': history})

def ajax_filtered_points(request):
    history = filter_points(request)
    return render(request, 'partials/points_table.html', {'history': history})

import datetime
from django.utils.timezone import now

def filter_points(request):
    user = request.user
    today = now().date()

    search_query = request.GET.get('search', '').strip().lower()
    date_filter = request.GET.get('date_filter', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base queryset
    history_queryset = PointsHistory.objects.filter(user=user).select_related('action_type')

    # Apply date filtering
    if date_filter == 'last_week':
        last_week = today - datetime.timedelta(days=7)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_week)
    elif date_filter == 'last_month':
        last_month = today - datetime.timedelta(days=30)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_month)
    elif date_filter == 'last_year':
        last_year = today - datetime.timedelta(days=365)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_year)
    elif date_filter == 'custom' and start_date and end_date:
        try:
            start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            history_queryset = history_queryset.filter(timestamp__date__range=(start_dt, end_dt))
        except ValueError:
            pass  # invalid date inputs are ignored

    # Convert to data list with readable formatting
    history_data = [
        {
            'timestamp': h.timestamp.strftime('%d/%m/%y, %H:%M'),
            'action_type': h.action_type.action_type.title() if h.action_type else 'Unknown',
            'points': h.points,
            'status': 'Completed'  # You may change based on logic
        }
        for h in history_queryset.order_by('-timestamp')
    ]

    # Search filter applied to data list
    if search_query:
        history_data = [
            entry for entry in history_data
            if search_query in entry['action_type'].lower()
            or search_query in entry['timestamp'].lower()
            or search_query in entry['status'].lower()
        ]

    return history_data
