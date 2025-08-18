from datetime import timedelta, datetime
from django.db.models import Q
from django.utils import timezone
from .models import Coupon

def get_saved_coupons_for_user(user, query='', date_range='', start=None, end=None, limit=None):
    filters = Q(advertiser=user)
    if query:
        filters &= (
            Q(category__name__icontains=query) |
            Q(brand_name__name__icontains=query) |
            Q(validity__icontains=query)
        )

    now = timezone.now()
    if date_range == "1 week":
        filters &= Q(created_at__gte=now - timedelta(weeks=1))
    elif date_range == "1 month":
        filters &= Q(created_at__gte=now - timedelta(days=30))
    elif date_range == "1 year":
        filters &= Q(created_at__gte=now - timedelta(days=365))
    elif date_range == "custom" and start and end:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            filters &= Q(created_at__range=(start_date, end_date))
        except Exception:
            pass

    coupons = Coupon.objects.filter(filters, saved=True).order_by('-created_at')
    if limit:
        coupons = coupons[:limit]
    return coupons