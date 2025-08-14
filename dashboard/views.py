from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Sum, Count, DecimalField, Q
from django.utils import timezone
from .utils import dashboard_login_required, get_common_context, get_theme_colors
from .models import SettingMenu, CouponPerformance,  CalendarEvent
from registration.models import MedicalProviderProfile, NGOProfile, ClientProfile, AdvertiserProfile
from ngopost.models import NGOPost
from .models import TrendingCoupon
from donate.models import Donation
from django.shortcuts import render
from django.http import JsonResponse, Http404
import json
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from registration.models import ContactPerson
from django.db.models.functions import TruncDate
import random
from datetime import date
from coupon.utils import get_saved_coupons_for_user
from django.core.paginator import Paginator
from coupon.models import Coupon
import logging
import os
from django.shortcuts import get_object_or_404
logger = logging.getLogger(__name__)

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

        # Add theme colors
    context["theme_colors"] = get_theme_colors(user_type)

    # Add menu
    context["sidebar_menu"] = menu_items
    
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

## Saved Section Common
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
            'user_display_name': ngo_profile.ngo_name,
            'user_profile': user_profile,
            'menu_items': menu_items,
            'saved_posts': saved_posts,
            'query': query,  # To retain search input
            'limit': str(limit),  # To retain limit select
        })

        return render(request, "dashboard/saved_ngo.html", context)
    
    elif user.user_type == 'advertiser':
        advertiser_profile = AdvertiserProfile.objects.get(user=user)
        context.update({
            'advertiser_profile': advertiser_profile,
            'user_display_name': advertiser_profile.company_name,
            'user_profile': user,
            'user': user
        })
        # Normal page render
        return render(request, "dashboard/saved_advertiser.html", context)
    elif user.user_type == 'provider':
        provider_profile = MedicalProviderProfile.objects.get(user=user)
        context.update({
            'provider_profile': provider_profile,
            'user_display_name': provider_profile.company_name,
            'user_profile': user,
            'user': user
        })
        return render(request, "dashboard/saved_provider.html", context)


## FOR Advertiser Saved Coupon In Saved Section ##
@require_GET
@dashboard_login_required
def adv_saved_coupon_history(request):
    user = request.user_obj
    query = request.GET.get('query', '').strip()
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    date_range = request.GET.get('daterange', '').strip().lower()

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
    elif date_range == "custom":
        # Optional: handle custom start_date and end_date from request.GET
        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            filters &= Q(created_at__range=(start_date, end_date))
        except Exception:
            pass  # Invalid format, ignore or handle as needed
    saved_coupons = Coupon.objects.filter(filters, saved=True).order_by('-created_at')
    paginator = Paginator(saved_coupons, limit)
    page_obj = paginator.get_page(page)

    html = render_to_string("advertiser/partials/saved-coupon-history-table.html", {
        "saved_coupon_history": page_obj.object_list,
        'today': date.today(),
    })

    return JsonResponse({
        "html": html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
    })

@dashboard_login_required
@require_GET
def coupon_detail(request, coupon_id):
    user = request.user_obj
    try:
        coupon = Coupon.objects.get(id=coupon_id, advertiser=user)
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Coupon not found'}, status=404)

    try:
        data = {
            'id': coupon.id,
            'uploaded_by': coupon.advertiser.email if coupon.advertiser else '',
            'uploaded_on': coupon.created_at.strftime('%Y-%m-%d %H:%M:%S') if coupon.created_at else '',
            'title': getattr(coupon, 'title', ''),
            'description': getattr(coupon, 'description', ''),
            'category': getattr(coupon.category, 'name', '') if coupon.category else '',
            'brand_name': getattr(coupon.brand_name, 'name', '') if hasattr(coupon, 'brand_name') and coupon.brand_name else '',
            'offer_type': getattr(coupon.offer_type, 'name', '') if hasattr(coupon, 'offer_type') and coupon.offer_type else '',
            'max_redemptions': getattr(coupon, 'max_redemptions', 0),
            'redeemed_count': getattr(coupon, 'redeemed_count', 0),
            'validity': coupon.validity.strftime('%d/%m/%y,%H:%M') if getattr(coupon, 'validity', None) else '',
            'status': 'Active' if getattr(coupon, 'validity', None) and coupon.validity > timezone.now().date() else 'Expired',
            'image_url': coupon.image.url if getattr(coupon, 'image', None) else '',
            'age_group': getattr(coupon.age_group, 'name', '') if hasattr(coupon, 'age_group') and coupon.age_group else '',
            'gender': getattr(coupon.gender, 'name', '') if hasattr(coupon, 'gender') and coupon.gender else '',
            'city': getattr(coupon.city, 'name', '') if hasattr(coupon, 'city') and coupon.city else '',
            'spending_power': getattr(coupon.spending_power, 'name', '') if hasattr(coupon, 'spending_power') and coupon.spending_power else '',
        }
    except Exception as e:
        logger.error(f"Error building coupon detail data: {e}", exc_info=True)
        return JsonResponse({'error': 'Server error'}, status=500)
    return JsonResponse(data)

@dashboard_login_required
@require_GET
def export_saved_coupon_history(request):
    user = request.user_obj
    # date_range = request.GET.get('daterange', '').strip().lower()
    filters = Q(advertiser=user)
    saved_coupons = Coupon.objects.filter(filters, saved=True).order_by('-created_at')
    html = render_to_string("partials/export-saved-history-table.html", {
        "saved_coupon_history": saved_coupons,
        'today': date.today(),
    })

    return JsonResponse({
        "html": html,
        "total_items": saved_coupons.count(),  # Add this
    })

@dashboard_login_required
@require_GET
def platform_bill(request, coupon_id):
    user = request.user_obj
    try:
        coupon = Coupon.objects.get(id=coupon_id, advertiser=user, saved=True)
        profile = coupon.advertiser.advertiserprofile
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Coupon not found'}, status=404)
    try:
        data = {
            'id': coupon.id,
            'company_name': profile.company_name if profile else '',
            'company_address': profile.address if profile else '',
            'phone_number': coupon.advertiser.phone_number if coupon.advertiser else '',
            'uploaded_by': coupon.advertiser.email if coupon.advertiser else '',
            'uploaded_on': coupon.created_at.strftime('%Y-%m-%d %H:%M:%S') if coupon.created_at else '',
            'quantity': getattr(coupon, 'max_redemptions', 0),
            'validity': coupon.validity.strftime('%d/%m/%y,%H:%M') if getattr(coupon, 'validity', None) else '',
            'rate_per_display': getattr(coupon, 'rate_per_display', 0),
            'payment_method': getattr(coupon, 'payment_method', ''),
            'displays_per_coupon': getattr(coupon, 'displays_per_coupon', 0),
            'gst_amount': getattr(coupon, 'gst_amount', 0),
            'final_paid_amount': getattr(coupon, 'final_paid_amount', 0),

            ## Platform Company details
            'company': os.environ.get("COMPANY", ""),
            'gstin': os.environ.get("GSTIN", ""),
            'address': os.environ.get("ADDRESS", ""),
            # 'phone': os.environ.get("PHONE", ""),
            # 'email': os.environ.get("EMAIL", ""),
            # 'website': os.environ.get("WEBSITE", ""),
        }
    except Exception as e:
        logger.error(f"Error building coupon detail data: {e}", exc_info=True)
        return JsonResponse({'error': 'Server error'}, status=500)
    return JsonResponse(data)

@dashboard_login_required
@require_GET
def get_donation_history(request):
    user = request.user_obj

    # --- 2. If not POST, continue with GET listing logic ---
    query = request.GET.get('query', '').strip()
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    date_range = request.GET.get('daterange', '').strip().lower()
    saved_only = request.GET.get('saved_only', '').lower() == 'true'

    filters = Q(user=user)
    if query:
        filters &= (
            Q(ngopost__header__icontains=query) |
            Q(payment_status__icontains=query) |
            Q(ngopost__post_type__name__icontains=query)
        )

    now = timezone.now()
    if date_range == "1 week":
        filters &= Q(created_at__gte=now - timedelta(weeks=1))
    elif date_range == "1 month":
        filters &= Q(created_at__gte=now - timedelta(days=30))
    elif date_range == "1 year":
        filters &= Q(created_at__gte=now - timedelta(days=365))
    elif date_range == "custom":
        # Optional: handle custom start_date and end_date from request.GET
        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            filters &= Q(created_at__range=(start_date, end_date))
        except Exception:
            pass  # Invalid format, ignore or handle as needed
    if saved_only:
        filters &= Q(saved=True)
    donations = Donation.objects.filter(filters).order_by('-created_at')
    paginator = Paginator(donations, limit)
    page_obj = paginator.get_page(page)
    
    html = render_to_string("advertiser/partials/donate-history.html", {
        "donation_history": page_obj.object_list,
        'today': date.today(),
    })
    logger.info(f"User {user.id} fetched donation history: {query}")
    return JsonResponse({
        "html": html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,  # Add this
    })

# show data on receipt 
@dashboard_login_required    
def get_donate_bill(request, donation_id):
    donation = Donation.objects.select_related('ngopost__user__ngoprofile').get(id=donation_id)
    ngoprofile = donation.ngopost.user.ngoprofile
    
    # Get the related NGO user
    ngo_user = donation.ngopost.user
    
     # Try to get the ContactPerson for the NGO profile
    contact_person = ContactPerson.objects.filter(
        profile_type='ngo',
        profile_id=ngoprofile.id
    ).first()  # use .first() to avoid MultipleObjectsReturned


    response_data = {
        "receipt_no": donation.id,
        "payment_date": donation.payment_date.strftime("%d-%b-%Y"),
        "ngo_name": donation.ngopost.user.ngoprofile.ngo_name,
        "pan": donation.pan_number,
        "amount": f"₹{donation.amount}",
        "pay_mode": f"₹{donation.payment_method}",
        "address": f"{donation.ngopost.user.ngoprofile.address}, {donation.ngopost.user.ngoprofile.city}, {donation.ngopost.user.ngoprofile.state}, {donation.ngopost.user.ngoprofile.pincode}",
        "name": contact_person.name,
        "email": ngo_user.email,
    }

    return JsonResponse(response_data)


# show data on receipt 
@dashboard_login_required    
def get_platform_bill(request, donation_id):
    donation = Donation.objects.select_related('ngopost__user__ngoprofile').get(id=donation_id)
    ngoprofile = donation.ngopost.user.ngoprofile
    
    # Get the related NGO user
    ngo_user = donation.ngopost.user
    
    # Try to get the ContactPerson for the NGO profile
    contact_person = ContactPerson.objects.filter(
        profile_type='ngo',
        profile_id=ngoprofile.id
    ).first()  # use .first() to avoid MultipleObjectsReturned


    response_data = {
        "receipt_no": donation.id,
        "payment_date": donation.payment_date.strftime("%d-%b-%Y"),
        "ngo_name": donation.ngopost.user.ngoprofile.ngo_name,
        "pan": donation.pan_number,
        "gst": donation.gst,
        "amount": f"₹{donation.amount}",
        "pay_mode": f"₹{donation.payment_method}",
        "address": f"{donation.ngopost.user.ngoprofile.address}, {donation.ngopost.user.ngoprofile.city}, {donation.ngopost.user.ngoprofile.state}, {donation.ngopost.user.ngoprofile.pincode}",
        "name": contact_person.name,
        "email": ngo_user.email,
        "finalTotal": f"{(donation.amount + donation.gst):.2f}",
    }

    return JsonResponse(response_data)

@dashboard_login_required
@require_POST
def toggle_saved_donation(request):
    donation_id = request.POST.get('donation_id')
    action = request.POST.get('action')

    if not donation_id or action not in ['save', 'unsave']:
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

    try:
        donation = Donation.objects.get(id=donation_id, user=request.user_obj)
        donation.saved = (action == 'save')
        donation.save()

        logger.info(f"User {request.user_obj} set saved={donation.saved} for donation {donation_id} (action={action})")
        return JsonResponse({'success': True, 'saved': donation.saved})

    except Donation.DoesNotExist:
        logger.warning(f"Donation {donation_id} not found or does not belong to user {request.user_obj}")
        return JsonResponse({'success': False, 'error': 'Donation not found'}, status=404)

# csv 
@dashboard_login_required
@require_GET
def export_donation_history(request):
    user = request.user_obj
    # date_range = request.GET.get('daterange', '').strip().lower()
    filters = Q(user=user)
    # For export, we want to show all donations, not just saved ones
    donations = Donation.objects.filter(filters).order_by('-created_at')
    html = render_to_string("advertiser/partials/export-donate-history.html", {
        "donation_history": donations,
        'today': date.today(),
    })
    logger.info(f"Exporting donation history for user {user} with {donations.count()} records")
    return JsonResponse({
        "html": html,
        "total_items": donations.count(),  # Add this
    })


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
    context = get_common_context(request, user)
    if user.user_type == 'advertiser':
        advertiser_profile = AdvertiserProfile.objects.get(user=user)
        context.update({
            'advertiser_profile': advertiser_profile,
            'user_display_name': advertiser_profile.company_name,
            'user_profile': user,
            'user': user
        })
        # Normal page render
        return render(request, "dashboard/advertiser_advance.html", context)
    elif user.user_type == 'ngo':
        provider_profile = NGOProfile.objects.get(user=user)
        context.update({
            'provider_profile': provider_profile,
            'user_display_name': provider_profile.company_name,
            'user_profile': user,
            'user':user
        })
        return render(request, "dashboard/advertiser_advance.html", context)
    elif user.user_type == 'provider':
        provider_profile = MedicalProviderProfile.objects.get(user=user)
        context.update({
            'provider_profile': provider_profile,
            'user_display_name': provider_profile.company_name,
            'user_profile': user,
            'user':user
        })
        return render(request, "dashboard/advertiser_advance.html", context)


@dashboard_login_required
def cart(request):
    user = request.user_obj
    context = get_common_context(request, user)
    if user.user_type == 'advertiser':
        advertiser_profile = AdvertiserProfile.objects.get(user=user)
        context.update({
            'advertiser_profile': advertiser_profile,
            'user_display_name': advertiser_profile.company_name,
            'user_profile': user,
            'user': user
        })
        # Normal page render
        return render(request, "dashboard/cart.html", context)
    elif user.user_type == 'provider':
        provider_profile = MedicalProviderProfile.objects.get(user=user)
        context.update({
            'provider_profile': provider_profile,
            'user_display_name': provider_profile.company_name,
            'user_profile': user,
            'user':user
        })
        return render(request, "dashboard/cart.html", context)