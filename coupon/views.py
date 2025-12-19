from pathlib import Path
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Q
from django.views.decorators.http import require_GET, require_http_methods
from dashboard.utils import dashboard_login_required, get_common_context
from .models import (
    Coupon, CategoryOption, BrandOption, OfferTypeOption, CountryOption,
    StateOption, CityOption, PincodeOption, AgeOption, GenderOption, SpendingPowerOption, PaymentStatusEnum
)
from points.models import PointsActionType, PointsHistory
from registration.views import validate_and_save_file


BASE_DIR = Path(__file__).resolve().parent.parent

@dashboard_login_required
def coupon_view(request):
    user = request.user_obj
    context = get_common_context(request, user)
    if user.user_type == "pharmacy":
        return render(request, "pharmacy/pharmacy_coupon.html", context)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            # Extract and clean base fields
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            code = request.POST.get('code', '').strip()
            country = CountryOption.objects.filter(id=request.POST.get('country')).first()
            max_redemptions = request.POST.get('max_redemptions', '').strip()
            validity = request.POST.get('validity', '').strip()
            image_file = request.FILES.get('coupon_image', None)

            # Payment fields
            displays_per_coupon = request.POST.get('displays_per_coupon', '').strip()
            rate_per_display = request.POST.get('rate_per_display', '').strip()
            payment_method = request.POST.get('payment-method', '').strip()
            final_paid_amount = request.POST.get('final_paid_amount', '').strip()
            gst_amount = request.POST.get('gst_amount', '').strip()

            # --- Handle dropdowns dynamically ---
            mappings = {
                "category": (CategoryOption, "Category"),
                "brand_name": (BrandOption, "Brand Name"),
                "state": (StateOption, "State"),
                "city": (CityOption, "City"),
                "pincode": (PincodeOption, "Pincode"),
                "age_group": (AgeOption, "Age Group"),
                "gender": (GenderOption, "Gender"),
                "spending_power": (SpendingPowerOption, "Spending Power"),
                "offer_type": (OfferTypeOption, "Offer Type"),
            }

            resolved_data = {}
            for field, (model, label) in mappings.items():
                value = request.POST.get(field, "").strip()
                if not value or value.lower() == "custom":
                    error_msg = f"Please type valid value for {label}."
                    if is_ajax:
                        return JsonResponse({"error": error_msg})
                    messages.error(request, error_msg)
                    return render(request, "coupon.html", get_context_data(user, request.POST, [label]))

                if value.isdigit():
                    obj = model.objects.filter(id=int(value)).first()
                    if not obj:
                        error_msg = f"Invalid {label} selected."
                        if is_ajax:
                            return JsonResponse({"error": error_msg})
                        messages.error(request, error_msg)
                        return render(request, "coupon.html", get_context_data(user, request.POST, [label]))
                else:
                    normalized_value = value.strip().lower()
                    obj = model.objects.filter(name__iexact=normalized_value).first()
                    if not obj:
                        obj = model.objects.create(name=value.strip().title())

                resolved_data[field] = obj
            # --- Validate image ---
            image_path = None
            if image_file:
                image_path, error = validate_and_save_file(
                    image_file, 'coupon_images', 'Coupon Image', user_type='advertiser'
                )
                if error:
                    if is_ajax:
                        return JsonResponse({'error': error, 'missing_fields': ['Image']})
                    messages.error(request, error)
                    return render(request, 'coupon.html', get_context_data(user, request.POST, ['Image']))

            # --- Validate numeric fields ---
            try:
                max_redemptions_int = int(max_redemptions) if max_redemptions else 0
                displays_per_coupon_int = int(displays_per_coupon) if displays_per_coupon else 0
                rate_per_display_float = float(rate_per_display) if rate_per_display else 0.0
                final_paid_amount_float = float(final_paid_amount) if final_paid_amount else 0.0
                gst_amount_float = float(gst_amount) if gst_amount else 0.0
            except (ValueError, TypeError):
                error_msg = "Invalid numeric values provided. Please check your inputs."
                if is_ajax:
                    return JsonResponse({"error": error_msg})
                messages.error(request, error_msg)
                return render(request, "coupon.html", get_context_data(user, request.POST, []))

            # --- Validate validity date ---
            try:
                validity_obj = datetime.strptime(validity, '%d/%m/%Y').date() if validity else None
                if validity_obj and validity_obj < datetime.now().date():
                    error_msg = "Validity date cannot be in the past."
                    if is_ajax:
                        return JsonResponse({"error": error_msg})
                    messages.error(request, error_msg)
                    return render(request, "coupon.html", get_context_data(user, request.POST, []))
            except ValueError:
                error_msg = "Invalid date format. Please use DD/MM/YYYY format."
                if is_ajax:
                    return JsonResponse({"error": error_msg})
                messages.error(request, error_msg)
                return render(request, "coupon.html", get_context_data(user, request.POST, []))

            # --- Required fields check ---
            required_fields = {
                "Title": title,
                "Description": description,
                "Code": code,
                "Country": country,
                "Max Redemptions": max_redemptions,
                "Validity": validity,
                "Image": image_file,
                "Displays per Coupon": displays_per_coupon,
                "Rate per Display": rate_per_display,
                "Payment Method": payment_method,
            }
            missing_fields = [name for name, value in required_fields.items() if not value]
            if missing_fields:
                if is_ajax:
                    return JsonResponse({"missing_fields": missing_fields})
                messages.error(request, f"Please fill all required fields: {', '.join(missing_fields)}")
                return render(request, "coupon.html", get_context_data(user, request.POST, missing_fields))

            # --- Duplicate coupon code check ---
            if Coupon.objects.filter(code=code, advertiser=user).exists():
                error_msg = "A coupon with this code already exists for your account."
                if is_ajax:
                    return JsonResponse({"error": error_msg})
                messages.error(request, error_msg)
                return render(request, "coupon.html", get_context_data(user, request.POST, []))

            # --- Save Coupon ---
            coupon = Coupon(
                advertiser=user,
                title=title,
                description=description,
                code=code,
                country=country,
                category=resolved_data["category"],
                brand_name=resolved_data["brand_name"],
                state=resolved_data["state"],
                city=resolved_data["city"],
                pincode=resolved_data["pincode"],
                age_group=resolved_data["age_group"],
                gender=resolved_data["gender"],
                spending_power=resolved_data["spending_power"],
                offer_type=resolved_data["offer_type"],
                max_redemptions=max_redemptions_int,
                validity=validity_obj,
                image=image_path,
                displays_per_coupon=displays_per_coupon_int,
                rate_per_display=rate_per_display_float,
                payment_method=payment_method.upper(),
                payment_status=PaymentStatusEnum.PENDING,
                payment_details="",
                final_paid_amount=final_paid_amount_float,
                gst_amount=gst_amount_float,
            )
            print(1234567890, coupon)
            coupon.save()

            # --- Award points ---
            try:
                action_type_obj = PointsActionType.objects.get(action_type="Coupon")
                PointsHistory.objects.create(
                    user=user,
                    action_type=action_type_obj,
                    points=action_type_obj.default_points,
                )
            except PointsActionType.DoesNotExist:
                print("PointsActionType for 'Coupon' does not exist. No points awarded.")

            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": "Coupon created successfully!",
                    "redirect": f"{reverse('coupons')}?tab=history"
                })

            messages.success(request, "Coupon posted successfully!")

        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            if is_ajax:
                return JsonResponse({"error": error_msg})
            messages.error(request, error_msg)
            return render(request, "coupon.html", get_context_data(user, request.POST, []))

    context.update(get_context_data(user))
    return render(request, "coupon.html", context)

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
            'image_url': coupon.image if coupon.image else '',
            'age_group': getattr(coupon.age_group, 'name', '') if hasattr(coupon, 'age_group') and coupon.age_group else '',
            'gender': getattr(coupon.gender, 'name', '') if hasattr(coupon, 'gender') and coupon.gender else '',
            'city': getattr(coupon.city, 'name', '') if hasattr(coupon, 'city') and coupon.city else '',
            'spending_power': getattr(coupon.spending_power, 'name', '') if hasattr(coupon, 'spending_power') and coupon.spending_power else '',
        }
    except Exception as e:
        return JsonResponse({'error': 'Server error'}, status=500)
    return JsonResponse(data)

@dashboard_login_required
@require_GET
def platform_bill(request, coupon_id):
    user = request.user_obj
    try:
        coupon = Coupon.objects.get(id=coupon_id, advertiser=user)
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
            'company': settings.COMPANY_NAME,
            'gstin': settings.COMPANY_GSTIN,
            'address': settings.COMPANY_ADDRESS,
            # 'phone': os.environ.get("PHONE", ""),
            # 'email': os.environ.get("EMAIL", ""),
            # 'website': os.environ.get("WEBSITE", ""),
        }
    except Exception as e:
        return JsonResponse({'error': 'Server error'}, status=500)
    return JsonResponse(data)

@dashboard_login_required
@require_http_methods(["GET", "POST"])
def get_coupon_history(request):
    user = request.user_obj

    # --- 1. Handle Save/Unsave action if it's a POST ---
    if request.method == "POST":
        coupon_id = request.POST.get('coupon_id')
        action = request.POST.get('action')  # 'save' or 'unsave'
        try:
            coupon = Coupon.objects.get(id=coupon_id, advertiser=user)
            coupon.saved = (action == 'save')
            coupon.save()
            return JsonResponse({'success': True, 'saved': coupon.saved})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)

    # --- 2. If not POST, continue with GET listing logic ---
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
            pass

    coupons = Coupon.objects.filter(filters).order_by('-created_at')
    paginator = Paginator(coupons, limit)
    page_obj = paginator.get_page(page)

    html = render_to_string("partials/coupon-history-table.html", {
        "coupon_history": page_obj.object_list,
        'today': date.today(),
    })

    return JsonResponse({
        "html": html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,  # Add this
    })

@dashboard_login_required
@require_GET
def get_saved_coupon_history(request):
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

    html = render_to_string("partials/saved-coupon-history-table.html", {
        "saved_coupon_history": page_obj.object_list,
        'today': date.today(),
    })

    return JsonResponse({
        "html": html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
    })

def get_context_data(user, form_data=None, missing_fields=None):
    """Helper function to get context data for the template"""
    context = {
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
        'today': date.today(),
    }
    
    if form_data:
        context['form_data'] = form_data
    if missing_fields:
        context['missing_fields'] = missing_fields
        
    return context

@dashboard_login_required
@require_GET
def export_coupon_history(request):
    user = request.user_obj
    # date_range = request.GET.get('daterange', '').strip().lower()
    filters = Q(advertiser=user)
    coupons = Coupon.objects.filter(filters).order_by('-created_at')
    html = render_to_string("partials/export-history-table.html", {
        "coupon_history": coupons,
        'today': date.today(),
    })

    return JsonResponse({
        "html": html,
        "total_items": coupons.count(),  # Add this
    })

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