from django.shortcuts import render
from dashboard.utils import dashboard_login_required
from ngopost.models import NGOPost
from registration.models import NGOProfile, User, AdvertiserProfile, ClientProfile, MedicalProviderProfile
from django.http import JsonResponse
from django.utils import timezone
import uuid
from donate.models import Donation
from registration.views import validate_and_save_file
from settings.views import validate_and_save_file
from decimal import Decimal
from points.models import PointsActionType, PointsHistory
import logging

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from registration.models import ContactPerson, User
from dashboard.views import get_common_context
logger = logging.getLogger(__name__)

@dashboard_login_required
def donate_view(request):
    user = request.user_obj
    if user.user_type == 'advertiser':
        user_profile = AdvertiserProfile.objects.filter(user=user).first()
    elif user.user_type == 'client':
        user_profile = ClientProfile.objects.filter(user=user).first()
    elif user.user_type == 'provider':
        user_profile = MedicalProviderProfile.objects.filter(user=user).first()

    org_query = request.GET.get('org_query', '').strip().lower()
    donation_query = request.GET.get('donation_query', '').strip().lower()
    limit = request.GET.get('limit', '50')  # default to 50
    try:
        limit = int(limit)
    except ValueError:
        limit = 50  # fallback if user tampers with value

    # Get Ongoing posts
    ngo_posts = NGOPost.objects.filter(status=NGOPost.Status.ONGOING).select_related('user').order_by('-created_at')

    # Map user_id to profile
    user_ids = [post.user_id for post in ngo_posts]
    profiles = NGOProfile.objects.filter(user_id__in=user_ids)
    profile_map = {profile.user_id: profile for profile in profiles}

    # Attach profile info
    for post in ngo_posts:
        profile = profile_map.get(post.user_id)
        post.ngo_name = profile.ngo_name if profile else "NGO Name Not Found"
        post.website_url = profile.website_url if profile else ""

    # Filter ngo_posts by org_query
    if org_query:
        ngo_posts = [post for post in ngo_posts if
                     org_query in post.post_type.lower() or
                     org_query in post.ngo_name.lower()]

    # Limit the number of posts shown
    ngo_posts = ngo_posts[:limit]

    # Filter donations by donation_query
    donations = Donation.objects.filter(user=request.user_obj).select_related('ngopost', 'ngopost__user', 'ngopost__user__ngoprofile')
    if donation_query:
        donations = [d for d in donations if
                     donation_query in (d.ngopost.post_type.lower() if d.ngopost and d.ngopost.post_type else '') or
                     donation_query in (d.ngopost.user.ngoprofile.ngo_name.lower() if d.ngopost and d.ngopost.user and hasattr(d.ngopost.user, 'ngoprofile') and d.ngopost.user.ngoprofile.ngo_name else '')]
    context = get_common_context(request, request.user_obj)
    context.update({
        "ngo_posts": ngo_posts,
        "donations": donations,
        "org_query": org_query,
        "donation_query": donation_query,
        "limit": str(limit),
        'user_display_name': user_profile.company_name,
    })
    return render(request, "client/donate.html", context)

@dashboard_login_required
def donate_pay_view(request, post_id=None):
    post = None
    ngo_profile = None
    if post_id:
        try:
            post = NGOPost.objects.select_related('user').get(id=post_id)
            # Increment views
            post.views = (post.views or 0) + 1
            post.save(update_fields=['views'])
            ngo_profile = NGOProfile.objects.filter(user=post.user).first()
        except NGOPost.DoesNotExist:
            post = None
    if request.method == 'POST' and post:
        user = request.user_obj
        amount = float(request.POST.get('donation_amount', 0))
        if amount < 100:
            return JsonResponse({'error': 'Minimum donation is ₹100'}, status=400)
        # Prevent donations exceeding target amount
        if (post.donation_received or Decimal('0.00')) + Decimal(str(amount)) > post.target_donation:
            return JsonResponse({'error': 'Donation exceeds the target amount for this post.'}, status=400)
        # Enforce donation frequency
        freq = post.donation_frequency.lower()
        user_donations_count = Donation.objects.filter(ngopost=post, user=user).count()
        allowed = 1 if 'one' in freq else 2 if 'two' in freq else 3 if 'three' in freq else 1
        if user_donations_count >= allowed:
            return JsonResponse({'error': f'You can donate only {allowed} time(s) to this post.'}, status=400)
        platform_fee = round(amount * 0.02, 2)
        gst = round(platform_fee * 0.18, 2)
        amount_to_ngo = round(amount - platform_fee - gst, 2)
        pan_number = request.POST.get('pan_number', '')
        pan_document_file = request.FILES.get('pan_document')
        pan_document_path, error = validate_and_save_file(pan_document_file, 'donation_docs', 'PAN Document', user_type='common')
        if error:
            return JsonResponse({'error': error}, status=400)
        order_id = str(uuid.uuid4().hex[:8])
        transaction_id = str(uuid.uuid4().hex[:8])
        donation = Donation.objects.create(
            ngopost=post,
            user=user,
            amount=amount,
            payment_method='UPI',
            pan_number=pan_number,
            pan_document=pan_document_path,
            payment_status='Success',
            order_id=order_id,
            payment_date=timezone.now(),
            gst=gst,
            platform_fee=platform_fee,
            amount_to_ngo=amount_to_ngo,
            transaction_id=transaction_id
        )
        # Increment donation_received
        post.donation_received = (post.donation_received or Decimal('0.00')) + Decimal(str(amount))
        post.save(update_fields=['donation_received'])
        try:
            action_type_obj = PointsActionType.objects.get(action_type='Donate')
            PointsHistory.objects.create(
                user=user,
                action_type=action_type_obj,
                points=action_type_obj.default_points
            )
        except PointsActionType.DoesNotExist:
            logger.warning("PointsActionType for 'Donate' does not exist. No points awarded.")
        return JsonResponse({'success': True, 'order_id': order_id, 'transaction_id': transaction_id})
    return render(request, "client/donate-pay.html", {"post": post, "ngo_profile": ngo_profile})


@dashboard_login_required
def donation_history_ajax(request):
    donation_query = request.GET.get("donation_query", "").strip()
    page_number = int(request.GET.get("page", 1))

    donations = Donation.objects.filter(user=request.user_obj).select_related(
        'ngopost', 'ngopost__user', 'ngopost__user__ngoprofile'
    )

    if donation_query:
        donations = donations.filter(
            Q(ngopost__header__icontains=donation_query) |
            Q(ngopost__user__ngoprofile__ngo_name__icontains=donation_query)
        )

    paginator = Paginator(donations, 10)  # change to 10 or whatever you want later
    page_obj = paginator.get_page(page_number)

    donation_html = render_to_string("client/donate-history.html", {"donations": page_obj})

    return JsonResponse({
        "html": donation_html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages
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

  
# csv 
@dashboard_login_required
def export_donations_csv(request):
    donations = Donation.objects.filter(user=request.user_obj).select_related(
        'ngopost', 'ngopost__user', 'ngopost__user__ngoprofile'
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donation_history.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Date & Time", "Header", "NGO Name", "Post Type", "Amount", "Payment Status"
    ])

    for donation in donations:
        writer.writerow([
            donation.payment_date.strftime('%d/%m/%Y, %H:%M') if donation.payment_date else '',
            smart_str(donation.ngopost.header if donation.ngopost else ''),
            smart_str(donation.ngopost.user.ngoprofile.ngo_name if donation.ngopost and donation.ngopost.user and hasattr(donation.ngopost.user, 'ngoprofile') else ''),
            smart_str(donation.ngopost.post_type if donation.ngopost else ''),
            f"{donation.amount:.2f}",  # ✅ Amount only, no ₹ symbol
            donation.payment_status,
        ])

    return response

