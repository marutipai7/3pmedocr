from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .models import (
    NGOPost, 
    PostTypeOption, 
    DonationFrequencyOption, 
    CountryOption, 
    StateOption, 
    CityOption, 
    AgeOption, 
    GenderOption, 
    SpendingPowerOption
    )
import logging
from registration.views import validate_and_save_file
from dashboard.utils import dashboard_login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET, require_POST
from donate.models import Donation
from django.db.models import Q
from points.models import PointsActionType, PointsHistory
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from datetime import datetime
from django.core.paginator import Paginator

# Get an instance of a logger
logger = logging.getLogger(__name__)


@dashboard_login_required
def post_view(request):
    user = request.user_obj

    # GET request handling - load form data
    history_query = request.GET.get('history_query', '').strip().lower()
    saved_query = request.GET.get('saved_query', '').strip().lower()

    # Get limits with proper validation
    try:
        history_limit_int = int(request.GET.get('history_limit', '10'))
    except ValueError:
        history_limit_int = 10
    
    try:
        saved_limit_int = int(request.GET.get('saved_limit', '10'))
    except ValueError:
        saved_limit_int = 10

    # Base queries
    post_history = NGOPost.objects.filter(user=user).order_by('-created_at')
    saved_posts = NGOPost.objects.filter(user=user, saved=True)

    # Apply search filters
    if history_query:
        post_history = post_history.filter(
            Q(post_type__icontains=history_query) |
            Q(status__icontains=history_query) |
            Q(created_at__icontains=history_query)
        )
    if saved_query:
        saved_posts = saved_posts.filter(
            Q(post_type__icontains=saved_query) |
            Q(status__icontains=saved_query) |
            Q(created_at__icontains=saved_query)
        )

    # Apply limits
    post_history = post_history[:history_limit_int]
    saved_posts = saved_posts[:saved_limit_int]

    # Update post status and attach donations
    for post in post_history:
        if post.status == post.Status.ONGOING and post.end_date < datetime.now().date():
            post.update_status_if_needed()
        post.donation_list = Donation.objects.filter(ngopost=post).select_related('user').order_by('-payment_date')
    
    for post in saved_posts:
        if post.status == post.Status.ONGOING and post.end_date < datetime.now().date():
            post.update_status_if_needed()
        post.donation_list = Donation.objects.filter(ngopost=post).select_related('user').order_by('-payment_date')

    context = {
        'post_history': post_history,
        'saved_posts': saved_posts,
        'history_query': history_query,
        'saved_query': saved_query,
        'history_limit': str(history_limit_int),
        'saved_limit': str(saved_limit_int),
        'post_type_options': PostTypeOption.objects.filter(is_active=True),
        'donation_frequency_options': DonationFrequencyOption.objects.filter(is_active=True),
        'country_options': CountryOption.objects.filter(is_active=True),
        'state_options': StateOption.objects.filter(is_active=True),
        'city_options': CityOption.objects.filter(is_active=True),
        'age_options': AgeOption.objects.filter(is_active=True),
        'gender_options': GenderOption.objects.filter(is_active=True),
        'spending_power_options': SpendingPowerOption.objects.filter(is_active=True),
    }
    return render(request, 'post.html', context)



@dashboard_login_required
def post_history_ajax(request):
    user = request.user_obj
    query = request.GET.get('query', '').strip()
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    saved_only = request.GET.get('saved_only', '').lower() == 'true'

    filters = Q(user=user)

    if query:
        filters &= Q(status__icontains=query) | Q(header__icontains=query)

    if start_date:
        try:
            filters &= Q(created_at__date__gte=datetime.strptime(start_date, '%Y-%m-%d').date())
        except: pass

    if end_date:
        try:
            filters &= Q(created_at__date__lte=datetime.strptime(end_date, '%Y-%m-%d').date())
        except: pass

    if saved_only:
        filters &= Q(saved=True)

    posts = NGOPost.objects.filter(filters).order_by('-created_at')

    paginator = Paginator(posts, limit)
    page_obj = paginator.get_page(page)

    html = render_to_string("partials/post_history_rows.html", {
        "post_history": page_obj.object_list,
    })

    return JsonResponse({
        "html": html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
    })


@dashboard_login_required
@csrf_exempt
def save_ngo_post(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    user = request.user_obj  # You said this is set in middleware

    data = request.POST
    files = request.FILES.getlist('creatives[]')

    required_fields = [
        'header', 'description', 'tags', 'post_type', 'donation_frequency',
        'target_donation', 'country', 'state', 'city', 'pincode',
        'age', 'gender', 'spending_power', 'start-date', 'end-date'
    ]
    missing_fields = [f for f in required_fields if not data.get(f)]
    if len(files) == 0:
        missing_fields.append('creatives[]')

    if missing_fields:
        return JsonResponse({'error': 'Missing required fields', 'missing_fields': missing_fields}, status=400)

    try:
        post = NGOPost.objects.create(
            user=user,
            header=data['header'].strip()[:80],
            description=data['description'].strip()[:500],
            tags=data['tags'].strip()[:255],
            post_type=data['post_type'],
            donation_frequency=data['donation_frequency'],
            target_donation=data['target_donation'].replace('Rs', '').replace(',', ''),
            country=data['country'],
            state=data['state'],
            city=data['city'],
            pincode=data['pincode'],
            age_group=data['age'],
            gender=data['gender'],
            spending_power=data['spending_power'],
            start_date=datetime.strptime(data['start-date'], '%Y-%m-%d'),
            end_date=datetime.strptime(data['end-date'], '%Y-%m-%d'),
            creative1=files[0] if len(files) > 0 else None,
            creative2=files[1] if len(files) > 1 else None
        )

        return JsonResponse({'success': True, 'post_id': post.id, 'message':'NGO Post Saved.'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': 'Something went wrong.', 'message':'NGO Post not Saved.', 'details': str(e)}, status=500)
    

@dashboard_login_required
@require_GET
def post_detail(request, post_id):
    try:
        post = NGOPost.objects.get(id=post_id)
    except NGOPost.DoesNotExist:
        raise Http404('Post not found')
    # Get donations for this post
    donations = Donation.objects.filter(ngopost=post).select_related('user', 'user__userprofile').order_by('-payment_date')
    donation_list = []
    for d in donations:
        userprofile = getattr(d.user, 'userprofile', None)
        donation_list.append({
            'payment_date': d.payment_date.strftime('%d/%m/%y,%H:%M') if d.payment_date else '',
            'name': userprofile.name if userprofile and userprofile.name else (d.user.email if d.user else ''),
            'city': userprofile.city if userprofile and userprofile.city else '',
            'amount': str(d.amount),
        })
    data = {
        'id': post.id,
        'header': post.header,
        'description': post.description,
        'tags': post.tags,
        'post_type': post.post_type,
        'donation_frequency': post.donation_frequency,
        'target_donation': post.target_donation,
        'country': post.country,
        'state': post.state,
        'city': post.city,
        'pincode': post.pincode,
        'age_group': post.age_group,
        'gender': post.gender,
        'views': post.views if hasattr(post, 'views') else 0,
        'post_reference_id': post.id,  # or post.reference_id if you have a custom field
        'uploaded_by': post.user.email if post.user else '',
        'status': post.status if hasattr(post, 'status') else '',
        'donation_received': post.donation_received if hasattr(post, 'donation_received') else 0,
        'date_time': str(post.created_at) if hasattr(post, 'created_at') else '',
        'spending_power': post.spending_power,
        'start_date': str(post.start_date),
        'end_date': str(post.end_date),
        'creative1': post.creative1.url if post.creative1 else '',
        'creative2': post.creative2.url if post.creative2 else '',
        'donations': donation_list,
    }
    logger.info(f"AJAX Preview Data for post {post_id}: {data}")
    return JsonResponse(data)

@dashboard_login_required
@require_POST
def toggle_saved_post(request):
    post_id = request.POST.get('post_id')
    action = request.POST.get('action')

    if not post_id or action not in ['save', 'unsave']:
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

    try:
        post = NGOPost.objects.get(id=post_id, user=request.user_obj)
        post.saved = (action == 'save')
        post.save()

        logger.info(f"User {request.user_obj} set saved={post.saved} for post {post_id} (action={action})")
        return JsonResponse({'success': True, 'saved': post.saved})

    except NGOPost.DoesNotExist:
        logger.warning(f"Post {post_id} not found or does not belong to user {request.user_obj}")
        return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)

@dashboard_login_required
@require_POST
def update_post_status(request):
    post_id = request.POST.get('post_id')
    new_status = request.POST.get('status')
    try:
        post = NGOPost.objects.get(id=post_id, user=request.user_obj)
        post.status = new_status
        post.save()
        return JsonResponse({'success': True, 'status': post.status})
    except NGOPost.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)