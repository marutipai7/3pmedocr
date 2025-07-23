from django.shortcuts import render
from dashboard.utils import dashboard_login_required
from .models import PointsHistory,PointsActionType,PointsBadge,CouponClaimed
from coupon.models import Coupon
from collections import defaultdict
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
import json
import datetime
from django.db.models import Sum
from django.utils.timezone import now
from registration.models import User 
from django.db.models import Q
from django.core.paginator import Paginator



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

    # 🔍 Search & Filters - PREVIOUS DATA HERE OF filter_point
   

    return render(request, 'ngo_points.html', {
        'total_points': total_points,
        'action_points': action_points,
        'chart_labels': chart_labels,
        'chart_data': dict(chart_data),
        # 'history': history_data,
        'all_badges': all_badges,
        'badge': badge,
    })


 

def get_coupon_cards(request):
    # Join with category and brand using select_related
    couponss = Coupon.objects.select_related('category', 'brand_name').all()
    
    query = request.GET.get('search', '').strip().lower()
    if query:
        coupons = Coupon.objects.filter(
            Q(title__icontains=query) |
            Q(code__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand_name__name__icontains=query)
        ).select_related('category', 'brand_name')[:100]
    else:
        coupons = Coupon.objects.all()

    # Prepare the list of coupon data
    coupon_list = [
        {
            "title": coupon.title,
            "description": coupon.description,
            "code": coupon.code,
            "id":coupon.id,
            "category": coupon.category.name,
            "brand_name": coupon.brand_name.name,
            "max_redemptions":coupon.max_redemptions,
            "redeemed_count":coupon.redeemed_count

        }
        for coupon in coupons
    ]

    html = render_to_string("partials/coupon_cards.html", {"products": coupon_list})
    return JsonResponse({"html": html})



def get_popular_coupon_cards(request):
    # Fetch top 10 popular coupons based on redeemed_count
    coupons = (
        Coupon.objects.select_related("category", "brand_name")
        .all()
        .order_by("-redeemed_count")[:10]
    )

    coupon_data = []
    for c in coupons:
            redeemed = c.redeemed_count or 0
            max_redemptions = c.max_redemptions or 100  # fallback to avoid division by 0

            percent_used = int((redeemed / max_redemptions) * 100)

            coupon_data.append({
                "title": c.title[:20],
                "id":c.id,
                "description": c.description[:120],
                "category": c.category.name if c.category else "N/A",
                "brand_name": c.brand_name.name if c.brand_name else "N/A",
                "code": c.code,
                "redeemed_count": redeemed,
                "max_redemptions": max_redemptions,
                "percent_used": percent_used,
            })


    html = render_to_string("partials/coupon_card_layout.html", {"coupons": coupon_data})
    return JsonResponse({"html": html})






def points_history_view(request):
    context = filter_points(request)
    return render(request, 'partials/points_table.html', context)

def ajax_filtered_points(request):
    context = filter_points(request)
    return render(request, 'partials/points_table.html', context)


@dashboard_login_required
def filter_points(request):
    user = request.user_obj
    today = now().date()

    search_query = request.GET.get('search', '').strip().lower()
    date_filter = request.GET.get('date_filter', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    page = request.GET.get('page', 1)
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

    # Search filtering
    if search_query:
        history_queryset = history_queryset.filter(
            Q(action_type__action_type__icontains=search_query)
        )

    history_queryset = history_queryset.order_by('-timestamp')

    # Pagination
    paginator = Paginator(history_queryset, 5)  # 10 items per page
    page_obj = paginator.get_page(page)

    history_data = [
        {
            'timestamp': h.timestamp.strftime('%d/%m/%y, %H:%M'),
            'action_type': h.action_type.action_type.title() if h.action_type else 'Unknown',
            'points': h.points,
            'status': 'Completed'
        }
        for h in page_obj
    ]

    return {
        'data': history_data,
        'page_obj': page_obj,
    }

@csrf_exempt
@require_POST
@dashboard_login_required
def claim_coupon(request):
    try:
        data = json.loads(request.body)
        coupon_id = data.get('coupon_id')
        coupon = Coupon.objects.get(id=coupon_id)
        user = request.user_obj

        if CouponClaimed.objects.filter(user=user, coupon=coupon).exists():
            return JsonResponse({'status': 'already_claimed'})

        CouponClaimed.objects.create(
            user=user,
            coupon=coupon,
            expiry_date=coupon.validity
        )
        return JsonResponse({'status': 'success'})

    except Coupon.DoesNotExist:
        return JsonResponse({'status': 'coupon_not_found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@dashboard_login_required
def get_claimed_coupons(request):
    user = request.user_obj
    claimed_coupons = CouponClaimed.objects.filter(user=user).select_related('coupon')

    html = render_to_string("partials/coupon_claimed_table.html", {
        "claimed_coupons": claimed_coupons
    })

    return JsonResponse({"html": html})