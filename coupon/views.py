from django.shortcuts import render, redirect
from django.urls import reverse
from dashboard.utils import dashboard_login_required
from .models import (
    Coupon, CategoryOption, BrandOption, OfferTypeOption, CountryOption,
    StateOption, CityOption, PincodeOption, AgeOption, GenderOption, SpendingPowerOption
)
from django.http import JsonResponse, Http404
from django.contrib import messages
from datetime import datetime
import logging
from points.models import PointsActionType, PointsHistory
from registration.views import validate_and_save_file  # Assuming you have this function
from datetime import date
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone

logger = logging.getLogger(__name__)

@dashboard_login_required
def coupon_view(request):
    user = request.user_obj
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'  # Ensure always defined
        # Debugging: Print all POST and FILES data
        print('DEBUG: request.POST:', dict(request.POST))
        print('DEBUG: request.FILES:', request.FILES)
        for key in request.POST:
            print(f'DEBUG: POST {key} = {request.POST[key]}')
        for key in request.FILES:
            print(f'DEBUG: FILES {key} = {request.FILES[key]}')
        try:
            # Extract and clean data
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            code = request.POST.get('code', '').strip()
            category=CategoryOption.objects.filter(id=request.POST.get('category')).first()
            brand_name=BrandOption.objects.filter(id=request.POST.get('brand_name')).first()
            country=CountryOption.objects.filter(id=request.POST.get('country')).first()
            state=StateOption.objects.filter(id=request.POST.get('state')).first()
            city=CityOption.objects.filter(id=request.POST.get('city')).first()
            pincode=PincodeOption.objects.filter(id=request.POST.get('pincode')).first()
            age_group=AgeOption.objects.filter(id=request.POST.get('age_group')).first()
            gender=GenderOption.objects.filter(id=request.POST.get('gender')).first()
            spending_power=SpendingPowerOption.objects.filter(id=request.POST.get('spending_power')).first()
            offer_type=OfferTypeOption.objects.filter(id=request.POST.get('offer_type')).first()
            max_redemptions = request.POST.get('max_redemptions', '').strip()
            validity = request.POST.get('validity', '').strip()
            image_file = request.FILES.get('coupon_image', None)
            print('DEBUG: request.FILES:', request.FILES)
            print('DEBUG: coupon_image in FILES:', 'coupon_image' in request.FILES)
            # Payment related fields
            displays_per_coupon = request.POST.get('displays_per_coupon', '').strip()
            rate_per_display = request.POST.get('rate_per_display', '').strip()
            payment_method = request.POST.get('payment-method', '').strip()
            final_paid_amount = request.POST.get('final_paid_amount', '').strip()
            gst_amount = request.POST.get('gst_amount', '').strip()

            # Validate required fields
            required_fields = {
                'Title': title,
                'Description': description,
                'Code': code,
                'Category': category,
                'Brand Name': brand_name,
                'Country': country,
                'State': state,
                'City': city,
                'Pincode': pincode,
                'Age Group': age_group,
                'Gender': gender,
                'Spending Power': spending_power,
                'Offer Type': offer_type,
                'Max Redemptions': max_redemptions,
                'Validity': validity,
                'Image': image_file,
                'Displays per Coupon': displays_per_coupon,
                'Rate per Display': rate_per_display,
                'Payment Method': payment_method,
            }
            
            missing_fields = [name for name, value in required_fields.items() if not value]

            # Validate and save image file
            image_path = None
            if image_file:
                image_path, error = validate_and_save_file(image_file, 'coupon_images', 'Coupon Image', user_type='advertiser')
                if error:
                    if is_ajax:
                        return JsonResponse({'error': error, 'missing_fields': ['Image']})
                    messages.error(request, error)
                    return render(request, 'coupon.html', get_context_data(user, request.POST, ['Image']))

            # Validate numeric fields
            try:
                max_redemptions_int = int(max_redemptions) if max_redemptions else 0
                displays_per_coupon_int = int(displays_per_coupon) if displays_per_coupon else 0
                rate_per_display_float = float(rate_per_display) if rate_per_display else 0.0
                final_paid_amount_float = float(final_paid_amount) if final_paid_amount else 0.0
                gst_amount_float = float(gst_amount) if gst_amount else 0.0
            except (ValueError, TypeError) as e:
                error_msg = "Invalid numeric values provided. Please check your inputs."
                if is_ajax:
                    return JsonResponse({'error': error_msg})
                messages.error(request, error_msg)
                return render(request, 'coupon.html', get_context_data(user, request.POST, missing_fields))

            # Validate validity date
            try:
                validity_obj = datetime.strptime(validity, '%d/%m/%Y').date() if validity else None
                if validity_obj and validity_obj < datetime.now().date():
                    error_msg = "Validity date cannot be in the past."
                    if is_ajax:
                        return JsonResponse({'error': error_msg})
                    messages.error(request, error_msg)
                    return render(request, 'coupon.html', get_context_data(user, request.POST, missing_fields))
            except ValueError:
                error_msg = "Invalid date format. Please use DD/MM/YYYY format."
                if is_ajax:
                    return JsonResponse({'error': error_msg})
                messages.error(request, error_msg)
                return render(request, 'coupon.html', get_context_data(user, request.POST, missing_fields))

            # Check for missing fields
            if missing_fields:
                print('DEBUG: Missing fields:', missing_fields)  # Debug log
                if is_ajax:
                    return JsonResponse({'missing_fields': missing_fields})
                messages.error(request, f"Please fill all required fields: {', '.join(missing_fields)}")
                return render(request, 'coupon.html', get_context_data(user, request.POST, missing_fields))

            # Check for duplicate coupon code
            if Coupon.objects.filter(code=code, advertiser=user).exists():
                error_msg = "A coupon with this code already exists for your account."
                if is_ajax:
                    return JsonResponse({'error': error_msg})
                messages.error(request, error_msg)
                return render(request, 'coupon.html', get_context_data(user, request.POST, missing_fields))

            # Save Coupon
            coupon = Coupon(
                advertiser=user,
                title=title,
                description=description,
                code=code,
                category=category,
                brand_name=brand_name,
                country=country,
                state=state,
                city=city,
                pincode=pincode,
                age_group=age_group,
                gender=gender,
                spending_power=spending_power,
                offer_type=offer_type,
                max_redemptions=max_redemptions_int,
                validity=validity_obj,
                image=image_path,
                displays_per_coupon=displays_per_coupon_int,
                rate_per_display=rate_per_display_float,
                payment_method=payment_method,
                payment_status='Pending',
                payment_details='',
                final_paid_amount=final_paid_amount_float,
                gst_amount=gst_amount_float,
            )
            coupon.save()
            
            # Award points
            try:
                action_type_obj = PointsActionType.objects.get(action_type='Coupon')
                PointsHistory.objects.create(
                    user=user,
                    action_type=action_type_obj,
                    points=action_type_obj.default_points
                )
            except PointsActionType.DoesNotExist:
                logger.warning("PointsActionType for 'Coupon' does not exist. No points awarded.")
            
            logger.info(f"Successfully created coupon with ID: {coupon.id}")
            
            if is_ajax:
                return JsonResponse({'success': True, 
                'message': 'Coupon created successfully!',
                'redirect': f"{reverse('coupons')}?tab=history"})
            
            messages.success(request, "Coupon posted successfully!")
            # return redirect(f"{reverse('coupons')}?tab=history")

        except Exception as e:
            logger.error(f"Error creating coupon: {e}", exc_info=True)
            error_msg = f"An unexpected error occurred: {str(e)}"
            if is_ajax:
                return JsonResponse({'error': error_msg})
            messages.error(request, error_msg)
            return render(request, 'coupon.html', get_context_data(user, request.POST, missing_fields))

    return render(request, 'coupon.html', get_context_data(user))


@dashboard_login_required
@require_GET
def coupon_detail(request, coupon_id):
    import logging
    logger = logging.getLogger(__name__)
    user = request.user_obj
    try:
        coupon = Coupon.objects.get(id=coupon_id, advertiser=user)
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Coupon not found'}, status=404)

    try:
        data = {
            'id': coupon.id,
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

    logger.info(f"AJAX Preview Data for coupon {coupon_id}: {data}")
    return JsonResponse(data)


@dashboard_login_required
@require_POST
def toggle_saved_coupon(request):
    coupon_id = request.POST.get('coupon_id')
    action = request.POST.get('action')  # 'save' or 'unsave'
    try:
        coupon = Coupon.objects.get(id=coupon_id, advertiser=request.user_obj)
        if action == 'save':
            coupon.saved = True
        else:
            coupon.saved = False
        coupon.save()
        logger.info(f"User {request.user_obj} set saved={coupon.saved} for post {coupon_id} (action={action})")
        return JsonResponse({'success': True, 'saved': coupon.saved})
    except Coupon.DoesNotExist:
        logger.warning(f"User {request.user_obj} tried to {action} post {coupon_id} but it does not exist or does not belong to them.")
        return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)

def get_context_data(user, form_data=None, missing_fields=None):
    """Helper function to get context data for the template"""
    context = {
        'coupon_history': Coupon.objects.filter(advertiser=user).order_by('-created_at'),
        'category_options': CategoryOption.objects.filter(is_active=True),
        'brand_options': BrandOption.objects.filter(is_active=True),
        'offer_type_options': OfferTypeOption.objects.filter(is_active=True),
        'country_options': CountryOption.objects.filter(is_active=True),
        'state_options': StateOption.objects.filter(is_active=True),
        'city_options': CityOption.objects.filter(is_active=True),
        'pincode_options': PincodeOption.objects.filter(is_active=True),
        'age_options': AgeOption.objects.filter(is_active=True),
        'gender_options': GenderOption.objects.filter(is_active=True),
        'spending_power_options': SpendingPowerOption.objects.filter(is_active=True),
        'coupon_history': Coupon.objects.filter(advertiser=user).order_by('-created_at'),
        'saved_coupon': Coupon.objects.filter(advertiser=user, saved=True),
        'today': date.today(),
    }
    
    if form_data:
        context['form_data'] = form_data
    if missing_fields:
        context['missing_fields'] = missing_fields
        
    return context