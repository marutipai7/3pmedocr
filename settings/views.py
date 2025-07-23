import re
import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from maps.models import SearchHistory, SavedLocation
from dashboard.utils import dashboard_login_required
from registration.models import (
    User,
    NGOProfile,
    ClientProfile,
    ContactPerson,
    UserProfile,
    AdvertiserProfile,
    ClientType,
    AdService,
    AdvertiserType,
    AdServiceReq,MedicalProviderProfile
    )
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST, require_GET
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.db import transaction
import logging
from .models import UserColorScheme

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE = 5 * 1024 * 1024 

def load_country_codes():
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'countryCodes.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)
def is_file_clean(file_obj):
    return True

def validate_and_save_file(file_obj, subdir, field_label, user_type='common'):
    if not file_obj:
        return '', f"{field_label} is required."

    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return '', f"{field_label} must be a PDF or image file."

    if file_obj.size > MAX_FILE_SIZE:
        return '', f"{field_label} must be under 5MB."

    if not is_file_clean(file_obj):
        return '', f"{field_label} failed virus scan."

    # 👇 Now user_type is part of the path — flexible for all
    upload_dir = os.path.join(user_type + '_docs', subdir)
    os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_dir), exist_ok=True)
    filename = default_storage.save(os.path.join(upload_dir, file_obj.name), file_obj)
    return filename, None

@dashboard_login_required
def settings_page(request):
    user = request.user_obj
    context = {
        'email': user.email,
        'country_code': '+91',
        'phone_no': user.phone_number or '',
        'user_type': user.user_type,
        'created_at': user.created_at,
        'updated_at': user.updated_at,
        "inapp_notifications": user.inapp_notifications,
        "email_notifications": user.email_notifications,
        "push_notifications": user.push_notifications,
        "regulatory_alerts": user.regulatory_alerts,
        "promotions_and_offers": user.promotions_and_offers,
        "quite_mode": user.quite_mode,
        "quite_mode_start_time": user.quite_mode_start_time,
        "quite_mode_end_time": user.quite_mode_end_time,
    }
    try:
        user_profile = UserProfile.objects.get(user=user)
        context.update({
            'name': user_profile.name,
            'date_of_birth': user_profile.dob,
            'gender': user_profile.gender,
            'address': user_profile.address,
            'city': user_profile.city,
            'state': user_profile.state,
            'country': user_profile.country,
            'pincode': user_profile.pincode,
            'referral_code': user_profile.referral_code if user_profile.referral_code else "",
        })
    except UserProfile.DoesNotExist:
        pass

    # Load profile-type-specific data (optional)
    if user.user_type == 'advertiser':
        profile = AdvertiserProfile.objects.filter(user=user).first()
        profile_id = profile.id
        context.update({
                'company_name': profile.company_name,
                'advertiser_type': profile.advertiser_type,
                'all_types': ['Brand', 'Agency', 'Influencer','Agency' 'Other'],
                'services_interested': profile.ad_services_required,
                'all_services': ['Digital Marketing', 'Content Creation', 'Social Media Management', 'SEO', 'PPC Advertising', 'Influencer Marketing', 'Brand Strategy', 'Market Research'],
                'website_url': profile.website_url,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'country': profile.country,
                'pincode': profile.pincode,
                'description': profile.brand_description,
                'brand_image_path': profile.brand_image_path,
                'referral_code': profile.referral_code if profile.referral_code else "",
                'incorporation_number': profile.incorporation_number,
                'incorporation_doc_path': os.path.basename(profile.incorporation_doc_path),
                'gst_number': profile.gst_number,
                'gst_doc_path': os.path.basename(profile.gst_doc_path),
                'pan_number': profile.pan_number,
                'pan_doc_path': os.path.basename(profile.pan_doc_path),
                'tan_number': profile.tan_number,
                'tan_doc_path': os.path.basename(profile.tan_doc_path),
                'brand_image_path': os.path.basename(profile.brand_image_path),
            })
        contact_persons = ContactPerson.objects.filter(
            profile_type=user.user_type,
            profile_id=profile_id
        ).first()
        if contact_persons:
            context.update({
                'contact_name': contact_persons.name,
                'contact_phone_country_code': contact_persons.phone_country_code,
                'contact_phone_number': contact_persons.phone_number,
                'contact_role': contact_persons.role,
            })
        else:
            context.update({
                'contact_name': 'N/A',
                'contact_phone_country_code': '',
                'contact_phone_number': '',
                'contact_role': '',
            })
        return render(request, 'settings/setting_page_advertiser.html', context)
    
    elif user.user_type == 'client':
        profile = ClientProfile.objects.filter(user=user).first()
        profile_id = profile.id
        if profile:
            context.update({
                'company_name': profile.company_name,
                'company_type': profile.company_type,
                'all_types': ['Private Limited', 'Public Limited', 'Partnership', 'Sole Proprietorship', 'LLP',],
                'services_interested': profile.services_interested,
                'all_services': ['Digital Marketing', 'Content Creation', 'Social Media Management', 'SEO', 'PPC Advertising', 'Influencer Marketing', 'Brand Strategy', 'Market Research'],
                'website_url': profile.website_url,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'country': profile.country,
                'pincode': profile.pincode,
                'referral_code': profile.referral_code if profile.referral_code else "",
                'incorporation_number': profile.incorporation_number,
                'incorporation_doc_path': os.path.basename(profile.incorporation_doc_path),
                'gst_number': profile.gst_number,
                'gst_doc_path': os.path.basename(profile.gst_doc_path),
                'pan_number': profile.pan_number,
                'pan_doc_path': os.path.basename(profile.pan_doc_path),
                'tan_number': profile.tan_number,
                'tan_doc_path': os.path.basename(profile.tan_doc_path),
            })
        contact_persons = ContactPerson.objects.filter(
            profile_type=user.user_type,
            profile_id=profile_id
        ).first()
        context.update({
            'contact_name': contact_persons.name,
            'contact_phone_country_code': contact_persons.phone_country_code,
            'contact_phone_number': contact_persons.phone_number,
            'contact_role': contact_persons.role,
        })
        return render(request, 'settings/settings_page_client.html', context)
    elif user.user_type == 'ngo':
        profile = NGOProfile.objects.filter(user=user).first()
        profile_id = profile.id
        if profile:
            context.update({
                'ngo_name': profile.ngo_name,
                'ngo_services': profile.ngo_services,
                'all_services': ['Education', 'Healthcare', 'Poverty Relief', 'General AID'],
                'website_url': profile.website_url,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'country': profile.country,
                'pincode': profile.pincode,
                'ngo_registration_number': profile.ngo_registration_number,
                'ngo_registration_doc_path': os.path.basename(profile.ngo_registration_doc_path),
                'pan_number': profile.pan_number,
                'pan_doc_path': os.path.basename(profile.pan_doc_path),
                'gst_number': profile.gst_number,
                'gst_doc_path': os.path.basename(profile.gst_doc_path),
                'tan_number': profile.tan_number,
                'tan_doc_path': os.path.basename(profile.tan_doc_path),
                'section8_number': profile.section8_number,
                'section8_doc_path': os.path.basename(profile.section8_doc_path),
                'doc_12a_number': profile.doc_12a_number,
                'doc_12a_path': os.path.basename(profile.doc_12a_path),
                'brand_description': profile.brand_description,
                'brand_image_path': os.path.basename(profile.brand_image_path),
                'referral_code': profile.referral_code if profile.referral_code else "",
            })
            print(context)
        contact_persons = ContactPerson.objects.filter(
            profile_type=user.user_type,
            profile_id=profile_id
        ).first()
        context.update({
            'contact_name': contact_persons.name,
            'contact_phone_country_code': contact_persons.phone_country_code,
            'contact_phone_number': contact_persons.phone_number,
            'contact_role': contact_persons.role,
        })
        return render(request, 'settings/settings_page.html', context)
    elif user.user_type == 'provider':
        profile = MedicalProviderProfile.objects.filter(user=user).first()
        profile_id = profile.id
        if profile:
            context.update({
                'company_name': profile.company_name,
                'provider_type': profile.provider_type,
                'services_offered': profile.services_offered,
                'website_url': profile.website_url,
                'storefront_image_path': profile.storefront_image_path,
            })    
    print(f"Context for settings page: {context}")

    return render(request, 'settings/settings_page.html', context)


def get_base_context(user):
    context = {
        'email': user.email,
        'country_code': '+91',
        'phone_no': user.phone_number or '',
        'user_type': user.user_type,
        'created_at': user.created_at,
        'updated_at': user.updated_at,
        'inapp_notifications': user.inapp_notifications,
        'email_notifications': user.email_notifications,
        'push_notifications': user.push_notifications,
        'regulatory_alerts': user.regulatory_alerts,
        'promotions_and_offers': user.promotions_and_offers,
        'quite_mode': user.quite_mode,
        'quite_mode_start_time': user.quite_mode_start_time,
        'quite_mode_end_time': user.quite_mode_end_time,
    }

    user_profile = UserProfile.objects.filter(user=user).first()
    if user_profile:
        context.update({
            'name': user_profile.name,
            'date_of_birth': user_profile.dob,
            'gender': user_profile.gender,
            'address': user_profile.address,
            'city': user_profile.city,
            'state': user_profile.state,
            'country': user_profile.country,
            'pincode': user_profile.pincode,
            'referral_code': user_profile.referral_code or '',
        })

    return context

def handle_contact_person(profile_type, profile_id):
    contact = ContactPerson.objects.filter(profile_type=profile_type, profile_id=profile_id).first()
    return {
        'contact_name': contact.name if contact else 'N/A',
        'contact_phone_country_code': getattr(contact, 'phone_country_code', ''),
        'contact_phone_number': getattr(contact, 'phone_number', ''),
        'contact_role': getattr(contact, 'role', ''),
    }

def handle_advertiser_profile(user):
    profile = AdvertiserProfile.objects.filter(user=user).first()
    if not profile:
        return {}

    data = {
        'company_name': profile.company_name,
        'advertiser_type': profile.advertiser_type,
        'all_types': ['Brand', 'Agency', 'Influencer', 'Other'],
        'services_interested': profile.ad_services_required,
        'all_services': [...],  # same list as before
        'website_url': profile.website_url,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'country': profile.country,
        'pincode': profile.pincode,
        'description': profile.brand_description,
        'brand_image_path': os.path.basename(profile.brand_image_path),
        'referral_code': profile.referral_code or '',
        'incorporation_number': profile.incorporation_number,
        'incorporation_doc_path': os.path.basename(profile.incorporation_doc_path),
        'gst_number': profile.gst_number,
        'gst_doc_path': os.path.basename(profile.gst_doc_path),
        'pan_number': profile.pan_number,
        'pan_doc_path': os.path.basename(profile.pan_doc_path),
        'tan_number': profile.tan_number,
        'tan_doc_path': os.path.basename(profile.tan_doc_path),
    }
    data.update(handle_contact_person(user.user_type, profile.id))
    return data

def handle_client_profile(user):
    profile = ClientProfile.objects.filter(user=user).first()
    if not profile:
        return {}
    data = {
        'company_name': profile.company_name,
        'company_type': profile.company_type,
        'all_types': [...],  # company types
        'services_interested': profile.services_interested,
        'all_services': [...],  # same service list
        'website_url': profile.website_url,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'country': profile.country,
        'pincode': profile.pincode,
        'referral_code': profile.referral_code or '',
        'incorporation_number': profile.incorporation_number,
        'incorporation_doc_path': os.path.basename(profile.incorporation_doc_path),
        'gst_number': profile.gst_number,
        'gst_doc_path': os.path.basename(profile.gst_doc_path),
        'pan_number': profile.pan_number,
        'pan_doc_path': os.path.basename(profile.pan_doc_path),
        'tan_number': profile.tan_number,
        'tan_doc_path': os.path.basename(profile.tan_doc_path),
    }
    data.update(handle_contact_person(user.user_type, profile.id))
    return data

def handle_ngo_profile(user):
    profile = NGOProfile.objects.filter(user=user).first()
    if not profile:
        return {}
    data = {
        'ngo_name': profile.ngo_name,
        'ngo_services': profile.ngo_services,
        'all_services': [...],
        'website_url': profile.website_url,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'country': profile.country,
        'pincode': profile.pincode,
        'ngo_registration_number': profile.ngo_registration_number,
        'ngo_registration_doc_path': os.path.basename(profile.ngo_registration_doc_path),
        'pan_number': profile.pan_number,
        'pan_doc_path': os.path.basename(profile.pan_doc_path),
        'gst_number': profile.gst_number,
        'gst_doc_path': os.path.basename(profile.gst_doc_path),
        'tan_number': profile.tan_number,
        'tan_doc_path': os.path.basename(profile.tan_doc_path),
        'section8_number': profile.section8_number,
        'section8_doc_path': os.path.basename(profile.section8_doc_path),
        'doc_12a_number': profile.doc_12a_number,
        'doc_12a_path': os.path.basename(profile.doc_12a_path),
        'brand_description': profile.brand_description,
        'brand_image_path': os.path.basename(profile.brand_image_path),
        'referral_code': profile.referral_code or '',
    }
    data.update(handle_contact_person(user.user_type, profile.id))
    return data

def handle_provider_profile(user):
    profile = MedicalProviderProfile.objects.filter(user=user).first()
    return {
        'company_name': profile.company_name,
        'provider_type': profile.provider_type,
        'services_offered': profile.services_offered,
        'website_url': profile.website_url,
        'storefront_image_path': profile.storefront_image_path,
    } if profile else {}



@require_GET
@dashboard_login_required
def get_account_details(request):
    try:
        user = request.user_obj
        context = get_base_context(user)

        # Map user_type to its handler function
        user_type_handlers = {
            'ngo': handle_ngo_profile,
            'client': handle_client_profile,
            'advertiser': handle_advertiser_profile,
            'provider': handle_provider_profile,
        }

        handler_func = user_type_handlers.get(user.user_type)
        if handler_func:
            context.update(handler_func(user))
        type = request.GET.get('type', 'view')
        # load_country_codes
        context['country_codes'] = load_country_codes()
        context['all_types'] = AdvertiserType.objects.filter(is_active=True)
        context["all_services"] = AdServiceReq.objects.filter(is_active=True)
        
        if type == 'view':
            html = render_to_string('partials/account_details.html', context, request=request)
        elif  type == 'edit':
            html = render_to_string('partials/edit-account-details.html', context, request=request)

        return JsonResponse({'success': True, 'html': html})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading account details: {str(e)}'})


def logout_view(request):
    request.session.flush()  # clears all session data
    return redirect('/login/')



@require_POST
@dashboard_login_required
def update_notification_field(request):
    user = request.user_obj
    data = json.loads(request.body)
    field = data.get("field")
    value = data.get("value")
    if field in ["inapp_notifications", "email_notifications", "push_notifications", "regulatory_alerts", "promotions_and_offers", "quite_mode"]:
        setattr(user, field, value)
    elif field in ["quite_mode_start_time", "quite_mode_end_time"]:
        setattr(user, field, value if value else None)
    user.save()
    return JsonResponse({"status": "success"})

@dashboard_login_required
@require_POST
def update_user_document(request):
    user = request.user_obj
    user_type = user.user_type
    doc_type = request.POST.get('doc_type')
    file = request.FILES.get('document')

    if not doc_type or not file:
        return JsonResponse({'success': False, 'error': 'Missing document or type.'}, status=400)

    subdir_map = {
        'ngo_registration_doc': 'registration',
        'incorporation_doc': 'registration',
        'gst_doc': 'gst',
        'pan_doc': 'pan',
        'tan_doc': 'tan',
        'section8_doc': 'section8',
        'doc_12a': 'doc_12a',
        'brand_image': 'brand_image',
        'medical_license_doc': 'medical_license',
        'storefront_image': 'storefront_image',
    }
        
    upload_subdir = subdir_map.get(doc_type)
    if not upload_subdir:
        return JsonResponse({'success': False, 'error': 'Invalid document type.'}, status=400)

    file_path, error = validate_and_save_file(file, upload_subdir, doc_type.replace('_', ' ').title(), user_type=user_type)
    if error:
        return JsonResponse({'success': False, 'error': error}, status=400)

    profile_model = {
        'ngo': NGOProfile,
        'advertiser': AdvertiserProfile,
        'client': ClientProfile,
        'provider': MedicalProviderProfile,
    }.get(user_type)

    if not profile_model:
        return JsonResponse({'success': False, 'error': 'Invalid user type for document upload.'}, status=400)

    profile = profile_model.objects.filter(user=user).first()
    if not profile:
        return JsonResponse({'success': False, 'error': 'Profile not found.'}, status=404)

    doc_field_map = {
        'ngo_registration_doc': ('ngo_registration_doc_path', 'ngo_registration_doc_virus_scanned'),
        'incorporation_doc': ('incorporation_doc_path', 'incorporation_doc_virus_scanned'),
        'gst_doc': ('gst_doc_path', 'gst_doc_virus_scanned'),
        'pan_doc': ('pan_doc_path', 'pan_doc_virus_scanned'),
        'tan_doc': ('tan_doc_path', 'tan_doc_virus_scanned'),
        'section8_doc': ('section8_doc_path', 'section8_doc_virus_scanned'),
        'doc_12a': ('doc_12a_path', 'doc_12a_virus_scanned'),
        'brand_image': ('brand_image_path', 'brand_image_virus_scanned'),
        'medical_license_doc': ('medical_license_doc_path', 'medical_license_doc_virus_scanned'),
        'storefront_image': ('storefront_image_path', 'storefront_image_virus_scanned'),
    }

    doc_fields = doc_field_map.get(doc_type)
    if not doc_fields:
        return JsonResponse({'success': False, 'error': 'Unknown document type.'}, status=400)

    setattr(profile, doc_fields[0], file_path)
    setattr(profile, doc_fields[1], True)
    profile.save()

    return JsonResponse({'success': True, 'message': 'Document updated successfully.'})

@require_POST
@dashboard_login_required
def update_ngo_profile(request):
    data = request.POST
    errors={}
    user = request.user_obj
    
    # --- Basic Validations ---
    email = data.get("email")
    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."
    phone_number = data.get("phone")
    if not phone_number or not re.match(r"^\d{8,15}$", phone_number):
        errors["phone"] = "Enter a valid phone number (8-15 digits)."

    ngo_services = request.POST.getlist("services")
    if not ngo_services:
        errors["services"] = "Select at least one NGO service."
        
    
    # Validate address fields
    for field in ["ngo_name","address", "city", "state", "pincode", "country", "contact_name", "contact_phone_number"]:
        if not data.get(field):
            errors[field] = f"{field.capitalize()} is required."
        
    # Update User model
    user.email = request.POST.get('email')
    user.phone_country_code = request.POST.get('countryCodes')
    user.phone_number = request.POST.get('phone')
    user.save()
    
    if errors:
        print(f"Validation errors: {errors}")
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # Update NGOProfile
    ngo_profile = NGOProfile.objects.filter(user=user).first()
    if ngo_profile:
        ngo_profile.ngo_name = request.POST.get('ngo_name')
        ngo_profile.website_url = request.POST.get('website_url')
        ngo_profile.address = request.POST.get('address')
        ngo_profile.city = request.POST.get('city')
        ngo_profile.state = request.POST.get('state')
        ngo_profile.country = request.POST.get('country')
        ngo_profile.pincode = request.POST.get('pincode')
        ngo_profile.ngo_services = request.POST.getlist('services')
        ngo_profile.referral_code = request.POST.get('referral_code')
        ngo_profile.save()

    # Update ContactPerson (if exists)
    contact_person = ContactPerson.objects.filter(
        profile_type='ngo', profile_id=ngo_profile.id
    ).first()

    if contact_person:
        contact_person.name = request.POST.get('contact_name')
        contact_person.phone_country_code = request.POST.get('countryCodes')
        contact_person.phone_number = request.POST.get('contact_phone_number')
        contact_person.role = request.POST.get('contact_role')
        contact_person.save()

    return JsonResponse({"success": True, "message": "NGO profile updated successfully."})  # Redirect back to settings page after save
    
@require_POST
@dashboard_login_required
def update_advertiser_profile(request):
    try:
        post_data = request.POST
        user = request.user_obj  # Assuming you're using `request.user_obj` as set in your middleware

        with transaction.atomic():
            # --- Update User ---
            user.email = post_data.get('email', user.email)
            user.phone_number = post_data.get('phone', user.phone_number)
            user.save()

            # --- Update AdvertiserProfile ---
            advertiser_profile = get_object_or_404(AdvertiserProfile, user=user)
            advertiser_profile.company_name = post_data.get('company_name', advertiser_profile.company_name)
            advertiser_profile.advertiser_type = post_data.getlist('advertiser_type') or None
            advertiser_profile.ad_services_required = post_data.getlist('company_services') or None
            advertiser_profile.website_url = post_data.get('website_url')
            advertiser_profile.city = post_data.get('city')
            advertiser_profile.state = post_data.get('state')
            advertiser_profile.country = post_data.get('country')
            advertiser_profile.pincode = post_data.get('pincode')
            advertiser_profile.save()

            # --- Update ContactPerson (optional) ---
            contact_name = post_data.get('contact_name')
            contact_role = post_data.get('contact_role')
            contact_phone = post_data.get('contact_phone_number')

            if contact_name or contact_phone:
                contact, created = ContactPerson.objects.get_or_create(
                    profile_type='advertiser',
                    profile_id=advertiser_profile.id
                )
                contact.name = contact_name
                contact.role = contact_role
                contact.phone_number = contact_phone
                contact.phone_country_code = user.phone_country_code or '+91'  # Default if needed
                contact.save()

        return JsonResponse({'success': True, 'message': 'Advertiser profile updated successfully'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@dashboard_login_required
def update_client_profile(request):
    try:
        post_data = request.POST
        user = request.user_obj

        profile, _ = ClientProfile.objects.get_or_create(user=user)
        profile.company_name = post_data.get('company_name')
        profile.company_type = post_data.get('company_type')
        profile.website_url = post_data.get('website_url')
        profile.address = post_data.get('address')
        profile.city = post_data.get('city')
        profile.state = post_data.get('state')
        profile.pincode = post_data.get('pincode')
        profile.country = post_data.get('country')
        profile.services_interested = post_data.getlist('company_services') or []

        # Optional: Save phone if field exists
        profile.phone = post_data.get('phone')
        profile.phone_country_code = post_data.get('countryCodes')

        profile.save()

        return JsonResponse({'success': True, 'message': 'Client profile updated successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating profile: {str(e)}'})

@require_POST
@dashboard_login_required
def delete_account(request):
    user = request.user_obj
    data = json.loads(request.body)
    reason = data.get("reason", "No reason provided")

    # Log the reason somewhere, like a model or file (optional)
    print(f"Deleted account {user.email}. Reason: {reason}")

    # Soft delete: deactivate user
    user.is_active = False
    user.save(update_fields=["is_active"])
    # user.delete()
    request.session.flush()

    return JsonResponse({'status': 'account deleted'})

@require_POST
@dashboard_login_required
def clear_search_history(request):
    user = request.user_obj
    SearchHistory.objects.filter(user=user).delete()
    return JsonResponse({'status': 'search history cleared'})

@require_POST
@dashboard_login_required
def clear_saved_data(request):
    user = request.user_obj
    SavedLocation.objects.filter(user=user).delete()
    
    return JsonResponse({'status': 'saved data cleared'})

@dashboard_login_required
@require_POST
def change_password(request):
    user = request.user_obj
    current_password = request.POST.get('current_password')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')
    errors={}
    print(f"Current Password: {current_password}, New Password: {new_password}, Confirm Password: {confirm_password}")

    if not check_password(current_password, user.password):
        errors["current_password"] = "Current password is incorrect."
    if not current_password or len(current_password) < 8:
        errors["new_password"] = "Password is required (min 8 chars)."
    elif new_password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."
        
    if errors:
        print("Validation errors:", errors)
        return JsonResponse({"success": False, "errors": errors}, status=400)
    
    user.password = make_password(new_password)
    user.save()
    return JsonResponse({'success': 'Password changed successfully'})

@require_POST
@dashboard_login_required
def update_ngo_profile_extra(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    user = getattr(request, "user_obj", None)
    if not user:
        return JsonResponse({"success": False, "message": "Unauthorized."}, status=401)

    data = request.POST
    errors = {}


    # return JsonResponse({"stop": True})

    # --- Basic Validations ---
    email = data.get("email", "").strip()
    phone_number = data.get("phone", "").strip()
    country_code = data.get("countryCodes", "").strip()

    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."

    if not phone_number or not re.match(r"^\d{8,15}$", phone_number):
        errors["phone"] = "Enter a valid phone number (8-15 digits)."

    ngo_services = data.getlist("ngo_services")
    if not ngo_services:
        errors["services"] = "Select at least one NGO service."

    required_fields = [
        "ngo_name", "address", "city", "state", "pincode",
        "country", "contact_name", "contact_phone_number"
    ]

    for field in required_fields:
        if not data.get(field, "").strip():
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

    # If validation fails, return errors before saving anything
    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # --- Update User model ---
    user.email = email
    user.phone_country_code = country_code
    user.phone_number = phone_number
    user.save()

    # --- Update NGOProfile ---
    ngo_profile = NGOProfile.objects.filter(user=user).first()
    if ngo_profile:
        ngo_profile.ngo_name = data.get("ngo_name", "").strip()
        ngo_profile.website_url = data.get("website_url", "").strip()
        ngo_profile.address = data.get("address", "").strip()
        ngo_profile.city = data.get("city", "").strip()
        ngo_profile.state = data.get("state", "").strip()
        ngo_profile.country = data.get("country", "").strip()
        ngo_profile.pincode = data.get("pincode", "").strip()
        ngo_profile.ngo_services = ngo_services
        ngo_profile.referral_code = data.get("referral_code", "").strip()
        ngo_profile.save()

        # --- Update ContactPerson ---
        contact_person = ContactPerson.objects.filter(
            profile_type='ngo', profile_id=ngo_profile.id
        ).first()

        if contact_person:
            contact_person.name = data.get("contact_name", "").strip()
            contact_person.phone_country_code = country_code
            contact_person.phone_number = data.get("contact_phone_number", "").strip()
            contact_person.role = data.get("contact_role", "").strip()
            contact_person.save()

    return JsonResponse({"success": True, "message": "NGO profile updated successfully."})

@require_GET
@dashboard_login_required
def get_user_theme_api(request):
    user = request.user_obj
    user_type = None

    try:
        if hasattr(user, 'ngoprofile') and user.ngoprofile is not None:
            user_type = 'ngo'
        elif hasattr(user, 'advertiserprofile') and user.advertiserprofile is not None:
            user_type = 'advertiser'
        elif hasattr(user, 'clientprofile') and user.clientprofile is not None:
            user_type = 'client'
        elif hasattr(user, 'medicalproviderprofile') and user.medicalproviderprofile is not None:
            user_type = 'provider'
        elif hasattr(user, 'userprofile') and user.userprofile is not None:
             user_type = 'user'
        else:
            user_type = None 
            logger.warning(f"Theme API: No specific profile found for user {user.username}. User type could not be determined for theme.")

    except Exception as e:
        logger.error(f"ERROR: Exception during user profile determination for user {user.id} in theme API: {e}", exc_info=True)
        user_type = None 

    if not user_type:
        logger.error(f"Theme API: User '{user.username if hasattr(user, 'username') else user.id}' has no determined user type for theme. Aborting.")
        return JsonResponse(
            {"error": "User type for theme could not be determined. Please ensure your profile is complete."},
            status=400
        )

    #logger.info(f"Theme requested for user: {user.username if hasattr(user, 'username') else user.id}, determined type: {user_type}")

    try:
        color_scheme_obj = UserColorScheme.objects.get(user_type=user_type, is_active=True)
        return JsonResponse(color_scheme_obj.color_data) 

    except UserColorScheme.DoesNotExist:
        logger.warning(f"No active UserColorScheme found for type: {user_type}. Falling back to 'user' theme.")
        try:
            default_color_scheme_obj = UserColorScheme.objects.get(user_type='user', is_active=True)
            return JsonResponse(default_color_scheme_obj.color_data, status=200)

        except UserColorScheme.DoesNotExist:
            logger.error(f"No active UserColorScheme found for default 'user' type either. Returning server error for theme config.")
            return JsonResponse(
                {"error": "Site theme not configured for your user type or default. Contact admin."},
                status=500
            )

    except Exception as e:
        logger.exception(f"An unexpected error occurred while fetching UserColorScheme for {user.username if hasattr(user, 'username') else user.id}: {e}")
        return JsonResponse({"error": "An unexpected server error occurred while loading theme. Please try again."}, status=500)