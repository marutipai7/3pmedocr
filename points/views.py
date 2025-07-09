from django.shortcuts import render
from dashboard.utils import dashboard_login_required
from .models import PointsHistory,PointsActionType
from collections import defaultdict
import datetime
from django.db.models import Sum
from registration.models import User 
from django.db.models import Q



@dashboard_login_required
def points_dashboard(request):
    user = request.user_obj
    user_type = getattr(user, 'user_type', '').lower()

    if user_type == 'ngo':
        chart_action_types = ['map', 'referral', 'post']
    elif user_type == 'client':
        chart_action_types = ['map', 'referral', 'subscription']
    elif user_type == 'advertiser':
        chart_action_types = ['map', 'referral', 'coupon']
    else:
        chart_action_types = []

    all_actions = PointsActionType.objects.all()
    action_points = {
        action.action_type: PointsHistory.objects.filter(
            user_id=user.id, action_type=action
        ).aggregate(total=Sum('points'))['total'] or 0
        for action in all_actions
    }

    total_points = sum(action_points.values())

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

    return render(request, 'ngo_points.html', {
        'total_points': total_points,
        'action_points': action_points,
        'chart_labels': chart_labels,
        'chart_data': dict(chart_data),
        'history': history_data
    })