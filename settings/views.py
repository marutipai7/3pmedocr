import re
import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from maps.models import SearchHistory, SavedLocation
from dashboard.utils import dashboard_login_required, get_common_context
from registration.models import *
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.db import transaction
import logging
from coupon.models import Coupon
from donate.models import Donation
from ngopost.models import NGOPost

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

def validate_email_phone(post_data, errors):
    email = post_data.get("email", "").strip()
    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."

    phone_number = post_data.get("phone", "").strip()
    if not re.match(r"^\d{10}$", phone_number):
        errors["phone"] = "Enter a valid 10-digit Indian mobile number."

@dashboard_login_required
def settings_page(request):
    user = request.user_obj
    context = get_common_context(request, user)
    context.update(get_base_context(user))
    
    user_type_handlers = {
        'ngo': handle_ngo_profile,
        'client': handle_client_profile,
        'advertiser': handle_advertiser_profile,
        'pharmacy': handle_pharmacy_profile,
    }
    handler_func = user_type_handlers.get(user.user_type)
    if handler_func:
        context.update(handler_func(user))
    context['country_codes'] = load_country_codes()
    # print(context)
    return render(request, 'settings/settings_page.html', context)

def get_base_context(user):
    context = {
        'email': user.email,
        'country_code': user.phone_country_code,
        'phone_no': user.phone_number,
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
    return context

def handle_contact_person(profile_type, profile_id):
    contact = ContactPerson.objects.filter(profile_type=profile_type, profile_id=profile_id).first()
    return {
        'contact_name': contact.name,
        'contact_phone_country_code': contact.phone_country_code,
        'contact_phone_number': contact.phone_number,
        'contact_role': contact.role
    }

def handle_advertiser_profile(user):
    profile = AdvertiserProfile.objects.filter(user=user).first()
    all_types = AdvertiserType.objects.filter(is_active=True)
    all_services = AdServiceReq.objects.filter(is_active=True)
    data = {
        'company_name': profile.company_name,
        'advertiser_type': profile.advertiser_type,
        'all_types': all_types,
        'services_interested': profile.ad_services_required,
        'all_services': all_services,
        'website_url': profile.website_url,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'country': profile.country,
        'pincode': profile.pincode,
        'brand_description': profile.brand_description,
        'brand_image_path': os.path.basename(profile.brand_image_path),
        'referral_code': profile.referral_code,
        'incorporation_number': profile.incorporation_number,
        'incorporation_doc_path': os.path.basename(profile.incorporation_doc_path),
        'gst_number': profile.gst_number,
        'gst_doc_path': os.path.basename(profile.gst_doc_path),
        'pan_number': profile.pan_number,
        'pan_doc_path': os.path.basename(profile.pan_doc_path),
        'tan_number': profile.tan_number,
        'tan_doc_path': os.path.basename(profile.tan_doc_path),
    }
    data.update(handle_contact_person(user.user_type, user))
    return data

def handle_client_profile(user):
    profile = ClientProfile.objects.filter(user=user).first()
    all_types = ClientType.objects.filter(is_active=True)
    all_services = ClientService.objects.filter(is_active=True)

    data = {
        'company_name': profile.company_name,
        'company_type': profile.company_type,
        'all_types': all_types,
        'services_interested': profile.services_interested,
        'all_services': all_services,
        'website_url': profile.website_url,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'country': profile.country,
        'pincode': profile.pincode,
        'referral_code': profile.referral_code,
        'incorporation_number': profile.incorporation_number,
        'incorporation_doc_path': os.path.basename(profile.incorporation_doc_path),
        'gst_number': profile.gst_number,
        'gst_doc_path': os.path.basename(profile.gst_doc_path),
        'pan_number': profile.pan_number,
        'pan_doc_path': os.path.basename(profile.pan_doc_path),
        'tan_number': profile.tan_number,
        'tan_doc_path': os.path.basename(profile.tan_doc_path),
    }
    data.update(handle_contact_person(user.user_type, user))
    return data

def handle_ngo_profile(user):
    profile = NGOProfile.objects.filter(user=user).first()
    all_services = NGOService.objects.filter(is_active=True)
    data = {
        'ngo_name': profile.ngo_name,
        'ngo_services': profile.ngo_services,
        'all_services': all_services,
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
        'referral_code': profile.referral_code,
    }
    data.update(handle_contact_person(user.user_type, user))
    return data

def handle_pharmacy_profile(user):
    profile = PharmacyProfile.objects.filter(user=user).first()
    all_types = PharmacyType.objects.filter(is_active=True)
    all_services = PharmacyServices.objects.filter(is_active=True)
    all_workingdays = PharmacyWorkingDays.objects.filter(is_active=True)
    data = {
        'company_name': profile.company_name,
        'pharmacy_type': profile.pharmacy_type,
        'all_types': all_types,
        'services_offered': profile.services_offered,
        'all_services': all_services,
        'working_days': profile.working_days,
        'all_workingdays': all_workingdays,
        'website_url': profile.website_url,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'country': profile.country,
        'pincode': profile.pincode,
        'referral_code': profile.referral_code or '',
        'incorporation_number': profile.incorporation_number,
        'incorporation_doc_path': os.path.basename(profile.incorporation_doc_path) if profile.incorporation_doc_path else "",
        'gst_number': profile.gst_number,
        'gst_doc_path': os.path.basename(profile.gst_doc_path) if profile.gst_doc_path else "",
        'medical_license_number': profile.medical_license_number,
        'medical_license_doc_path': os.path.basename(profile.medical_license_doc_path) if profile.medical_license_doc_path else "",
        'pan_number': profile.pan_number,
        'pan_doc_path': os.path.basename(profile.pan_doc_path) if profile.pan_doc_path else "",
        'tan_number': profile.tan_number,
        'tan_doc_path': os.path.basename(profile.tan_doc_path) if profile.tan_doc_path else "",
        'storefront_image_path': os.path.basename(profile.storefront_image_path) if profile.storefront_image_path else "",
    }
    data.update(handle_contact_person(user.user_type, user))
    return data

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
        'incorporation_doc': 'incorporation',
        'gst_doc': 'gst',
        'pan_doc': 'pan',
        'tan_doc': 'tan',
        'section8_doc': 'section8',
        'doc_12a': 'doc_12a',
        'brand_image': 'brand_image',
        'medical_license_doc': 'medical_license',
        'storefront_image': 'store_front',
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
        'pharmacy': PharmacyProfile,
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
    
    validate_email_phone(data, errors)
    
    ngo_services = request.POST.get("ngo_services")
    if not ngo_services:
        errors["services"] = "Select at least one NGO service."
        
    # Validate address fields
    for field in ["ngo_name","address", "city", "state", "pincode", "country", "contact_name", "contact_phone_number"]:
        if not data.get(field):
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."
    
    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)
        
    with transaction.atomic():
    # Update User model
        user.email = request.POST.get('email')
        user.phone_country_code = request.POST.get('countryCodes')
        user.phone_number = request.POST.get('phone')
        user.save()

    # Update NGOProfile
        ngo_profile = NGOProfile.objects.filter(user=user).first()
        if ngo_profile:
            for field in ["ngo_name", "website_url", "address", "city", "state", "country", "pincode", "referral_code"]:
                setattr(ngo_profile, field, data.get(field))
            ngo_profile.ngo_services = NGOService.objects.get(name=data.get("ngo_services"))
            ngo_profile.save()
        contact_person = ContactPerson.objects.filter(profile_type='ngo', profile_id=user).first()

        if contact_person:
            contact_person.name = request.POST.get('contact_name')
            contact_person.phone_country_code = request.POST.get('contact_countryCodes')
            contact_person.phone_number = request.POST.get('contact_phone_number')
            contact_person.role = request.POST.get('contact_role')
            contact_person.save()

    return JsonResponse({"success": True, "message": "NGO profile updated successfully."})
    
@require_POST
@dashboard_login_required
def update_advertiser_profile(request):
    post_data = request.POST
    errors = {}
    user = request.user_obj  
    
    validate_email_phone(post_data, errors)
    
    required_fields = ["company_name", "phone","address", "city", "state", "country", "pincode", "contact_name", "contact_phone_number", "contact_role"]
    for field in required_fields:
        if not post_data.get(field):
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    try:
        with transaction.atomic():
            # --- Update User ---
            # user.email = post_data.get('email')
            user.phone_country_code = post_data.get("countryCodes")
            user.phone_number = post_data.get("phone")
            user.save()

            # --- Update AdvertiserProfile ---
            advertiser_profile = get_object_or_404(AdvertiserProfile, user=user)
            advertiser_profile.company_name = post_data.get("company_name")
            advertiser_profile.advertiser_type = AdvertiserType.objects.get(name=post_data.get("advertiser_type"))
            advertiser_profile.ad_services_required = AdServiceReq.objects.get(name=post_data.get("company_services") )
            advertiser_profile.website_url = post_data.get("website_url")
            advertiser_profile.address = post_data.get("address")
            advertiser_profile.city = post_data.get("city")
            advertiser_profile.state = post_data.get("state")
            advertiser_profile.country = post_data.get("country")
            advertiser_profile.pincode = post_data.get("pincode")
            advertiser_profile.save()

            # --- Update or Create ContactPerson ---
            contact_name = post_data.get("contact_name")
            contact_phone = post_data.get("contact_phone_number")
            if contact_name or contact_phone:
                contact, _ = ContactPerson.objects.get_or_create(
                    profile_type="advertiser",
                    profile_id=user
                )
                contact.name = contact_name
                contact.role = post_data.get("contact_role")
                contact.phone_country_code = post_data.get("contact_countryCodes")
                contact.phone_number = contact_phone
                contact.save()

        return JsonResponse({'success': True, 'message': 'Advertiser profile updated successfully'})
    
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@require_POST
@dashboard_login_required
def update_client_profile(request):
    post_data = request.POST
    errors = {}
    user = request.user_obj
    validate_email_phone(post_data, errors)

    # Required fields
    required_fields = ["company_name", "company_type", "address", "city", "state", "pincode", "country"]
    for field in required_fields:
        if not post_data.get(field):
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)
    try:
        with transaction.atomic():
            # Update User model
            user.email = post_data.get('email')
            user.phone_country_code = post_data.get('countryCodes', "+91")
            user.phone_number = post_data.get('phone')
            user.save()
            
            # --- Update ClientProfile ---
            profile = get_object_or_404(ClientProfile, user=user)
            profile.company_name = post_data.get("company_name")
            profile.company_type = ClientType.objects.get(name=post_data.get("company_type"))
            profile.website_url = post_data.get("website_url")
            profile.address = post_data.get("address")
            profile.city = post_data.get("city")
            profile.state = post_data.get("state")
            profile.pincode = post_data.get("pincode")
            profile.country = post_data.get("country")
            profile.services_interested = ClientService.objects.get(name=post_data.get("company_services")) 
            profile.phone = post_data.get("phone")
            profile.phone_country_code = post_data.get("countryCodes")
            profile.save()
            
            contact_name = post_data.get("contact_name")
            contact_phone = post_data.get("contact_phone_number")
            if contact_name or contact_phone:
                contact, _ = ContactPerson.objects.get_or_create(
                    profile_type="advertiser",
                    profile_id=user
                )
                contact.name = contact_name
                contact.role = post_data.get("contact_role")
                contact.phone_country_code = post_data.get("contact_countryCodes")
                contact.phone_number = contact_phone
                contact.save()

        return JsonResponse({'success': True, 'message': 'Client profile updated successfully.'})
    except Exception as e:
        import traceback
        print(traceback)
        return JsonResponse({'success': False, 'message': f'Error updating profile: {str(e)}'})

@require_POST
@dashboard_login_required
def update_pharmacy_profile(request):
    post_data = request.POST
    errors = {}
    user = request.user_obj  

    # --- Validate ---
    validate_email_phone(post_data, errors)
    required_fields = ["company_name", "city", "state", "country", "pincode"]
    for field in required_fields:
        if not post_data.get(field):
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    try:
        with transaction.atomic():
            # --- Update User ---
            user.email = post_data.get('email')
            user.phone_country_code = post_data.get("countryCodes")
            user.phone_number = post_data.get("phone")
            user.save()

            # --- Update Pharmacy Profile ---
            pharmacy_profile = get_object_or_404(PharmacyProfile, user=user)
            pharmacy_profile.company_name = post_data.get("company_name")
            pharmacy_profile.website_url = post_data.get("website_url")
            pharmacy_profile.address = post_data.get("address")
            pharmacy_profile.city = post_data.get("city")
            pharmacy_profile.state = post_data.get("state")
            pharmacy_profile.country = post_data.get("country")
            pharmacy_profile.pincode = post_data.get("pincode")

            pharmacy_type_value = post_data.get("pharmacy_type")
            if pharmacy_type_value:
                pharmacy_profile.pharmacy_type = get_object_or_404(PharmacyType, name=pharmacy_type_value)
            services_offered_value = post_data.get("services_offered")
            if services_offered_value:
                pharmacy_profile.services_offered = get_object_or_404(PharmacyServices, name=services_offered_value)
            working_days_value = post_data.get("working_days")
            if working_days_value:
                pharmacy_profile.working_days = get_object_or_404(PharmacyWorkingDays, name=working_days_value)

            pharmacy_profile.save()

            # --- Update or Create ContactPerson ---
            contact_name = post_data.get("contact_name")
            contact_phone = post_data.get("contact_phone_number")
            if contact_name or contact_phone:
                contact, _ = ContactPerson.objects.get_or_create(
                    profile_type="pharmacy",
                    profile_id=user
                )
                contact.name = contact_name
                contact.role = post_data.get("contact_role")
                contact.phone_country_code = post_data.get("contact_countryCodes")
                contact.phone_number = contact_phone
                contact.save()

        return JsonResponse({'success': True, 'message': 'Pharmacy profile updated successfully'})
    
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@require_POST
@dashboard_login_required
def delete_account(request):
    user = request.user_obj
    data = json.loads(request.body)
    reason = data.get("reason", "No reason provided")
    logger.info(msg=f"Deleted account {user.email}. Reason: {reason}")

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

    if user.user_type == 'advertiser':
        Coupon.objects.filter(user=user, saved=True).update(saved=False)
        Donation.objects.filter(user=user, saved=True).update(saved=False)

    if user.user_type == 'ngo':
        NGOPost.objects.filter(user=user, saved=True).update(saved=False)

    if user.user_type == "pharmacy":
        Donation.objects.filter(user=user, saved=True).update(saved=False)

    return JsonResponse({'status': 'saved data cleared'})

@dashboard_login_required
@require_POST
def change_password(request):
    try:
        user = request.user_obj
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        errors={}
        error=''
        if not current_password or len(current_password) <= 8:
            errors["new_password"] = "Password is required (min 8 chars)."
            error = "Password is required (min 8 chars)."
        if not check_password(current_password, user.password):
            errors["current_password"] = "Current password is incorrect."
            error = "Current password is incorrect."
        elif new_password != confirm_password:
            errors["confirm_password"] = "Passwords do not match."
            error = "Passwords do not match."
            
        if errors:
            return JsonResponse({"success": False, "errors": errors, "message": error})
        
        user.password = make_password(new_password)
        user.save()
        return JsonResponse({'success': True, 'message': 'Password changed successfully', "errors" : ''})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': f'Error updating password: {str(e)}', "message" : ''})
