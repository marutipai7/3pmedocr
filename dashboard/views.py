from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone
from .utils import dashboard_login_required
from .models import SettingMenu
from registration.models import NGOProfile, ClientProfile, AdvertiserProfile
from ngopost.models import NGOPost
from django.db.models import Q

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
                'total_posts': posts_qs.count(),
                'total_views': posts_qs.aggregate(Sum('views'))['views__sum'] or 0,
                'total_target': posts_qs.aggregate(Sum('target_donation'))['target_donation__sum'] or 0,
                'total_received': posts_qs.aggregate(Sum('donation_received'))['donation_received__sum'] or 0,
                'trending_posts': posts_qs.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).order_by('-views')[:4],
            })
            return render(request, "dashboard/home.html", context)

        elif user_type == 'client':
            client_profile = ClientProfile.objects.get(user=user)
            context.update({
                'client_profile': client_profile,
                # Add relevant client data if any, e.g. campaigns
            })
            return render(request, "dashboard/home.html", context)

        elif user_type == 'advertiser':
            advertiser_profile = AdvertiserProfile.objects.get(user=user)
            context.update({
                'advertiser_profile': advertiser_profile,
                # Add advertiser-specific context
            })
            return render(request, "dashboard/home.html", context)

        else:
            return render(request, "dashboard/not_found.html")

    except Exception as e:
        # Log e if needed
        return render(request, "dashboard/not_found.html")


def logout_view(request):
    request.session.flush()  # clears all session data
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