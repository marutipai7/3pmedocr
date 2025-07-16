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
# Get an instance of a logger
logger = logging.getLogger(__name__)


@dashboard_login_required
def post_view(request):
    user = request.user_obj
    
    if request.method == 'POST':
        try:
            # Extract and validate data
            header = request.POST.get('header', '').strip()
            description = request.POST.get('description', '').strip()
            tags = request.POST.get('tags', '').strip()
            post_type = request.POST.get('post_type', '').strip()
            donation_frequency = request.POST.get('donation_frequency', '').strip()
            target_donation = request.POST.get('target_donation', '').strip()
            
            country = request.POST.get('country', '').strip()
            state = request.POST.get('state', '').strip()
            city = request.POST.get('city', '').strip()
            pincode = request.POST.get('pincode', '').strip()

            age_group = request.POST.get('age', '').strip()
            gender = request.POST.get('gender', '').strip()
            spending_power = request.POST.get('spending_power', '').strip()
            start_date = request.POST.get('start-date','').strip()
            end_date = request.POST.get('end-date','').strip()

            creative_files = request.FILES.getlist('creatives')
            creative1_file = creative_files[0] if len(creative_files) > 0 else None
            creative2_file = creative_files[1] if len(creative_files) > 1 else None

            # Basic validation
            required_fields = {
                'Header': header, 'Description': description, 'Tags': tags,
                'Post Type': post_type, 'Target Donation': target_donation,
                'Country': country, 'State': state, 'City': city, 'Pincode': pincode,
                'Start Date': start_date, 'End Date': end_date,
                'Creative Upload': creative1_file
            }
            missing_fields = [name for name, value in required_fields.items() if not value]
            
            # Check if request is AJAX
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            # File validation
            creative1_path, error = validate_and_save_file(creative1_file, 'post_creatives', 'Creative 1', user_type='ngo')
            if error:
                if is_ajax:
                    return JsonResponse({'error': error, 'missing_fields': ['Creative Upload']})
                messages.error(request, error)
                return render(request, 'post.html', {'form_data': request.POST})

            creative2_path = None
            if creative2_file:
                creative2_path, error = validate_and_save_file(creative2_file, 'post_creatives', 'Creative 2', user_type='ngo')
                if error:
                    if is_ajax:
                        return JsonResponse({'error': error, 'missing_fields': ['Creative Upload']})
                    messages.error(request, error)
                    return render(request, 'post.html', {'form_data': request.POST})

            # Return validation errors for AJAX
            if is_ajax and missing_fields:
                return JsonResponse({'missing_fields': missing_fields})
            
            # Return validation errors for normal POST
            if missing_fields:
                messages.error(request, f"Please fill all required fields: {', '.join(missing_fields)}")
                return render(request, 'post.html', {'form_data': request.POST})

            # Save post (ONLY ONCE)
            post = NGOPost(
                user=user,
                header=header,
                description=description,
                tags=tags,
                post_type=post_type,
                donation_frequency=donation_frequency,
                target_donation=target_donation.replace('Rs', '').replace(',', '').strip(),
                country=country,
                state=state,
                city=city,
                pincode=pincode,
                age_group=age_group,
                gender=gender,
                spending_power=spending_power,
                start_date=start_date,
                end_date=end_date,
                creative1=creative1_path,
                creative2=creative2_path
            )
            post.save()
            
            # Award points
            try:
                action_type_obj = PointsActionType.objects.get(action_type='Post')
                PointsHistory.objects.create(
                    user=user,
                    action_type=action_type_obj,
                    points=action_type_obj.default_points
                )
            except PointsActionType.DoesNotExist:
                logger.warning("PointsActionType for 'Post' does not exist. No points awarded.")
            
            logger.info(f"Successfully saved new post with ID: {post.id}")
            
            # Return appropriate response
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Post created successfully!'})
            else:
                messages.success(request, "Your post has been successfully created!")
                return redirect('posts')

        except (ValueError, TypeError) as e:
            logger.error(f"Error processing form data: {e}", exc_info=True)
            error_msg = f"Invalid data submitted. Please check your inputs. Error: {e}"
            if is_ajax:
                return JsonResponse({'error': error_msg})
            messages.error(request, error_msg)
        except Exception as e:
            logger.error(f"An unexpected error occurred in post_view: {e}", exc_info=True)
            error_msg = f"An unexpected error occurred: {e}"
            if is_ajax:
                return JsonResponse({'error': error_msg})
            messages.error(request, error_msg)

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
    action = request.POST.get('action')  # 'save' or 'unsave'
    try:
        post = NGOPost.objects.get(id=post_id, user=request.user_obj)
        if action == 'save':
            post.saved = True
        else:
            post.saved = False
        post.save()
        logger.info(f"User {request.user_obj} set saved={post.saved} for post {post_id} (action={action})")
        return JsonResponse({'success': True, 'saved': post.saved})
    except NGOPost.DoesNotExist:
        logger.warning(f"User {request.user_obj} tried to {action} post {post_id} but it does not exist or does not belong to them.")
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