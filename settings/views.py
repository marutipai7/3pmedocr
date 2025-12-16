import os
import re
import json
import uuid
from decimal import Decimal
from datetime import date, datetime, timedelta
from collections import defaultdict
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db import transaction
from django.db.models import Q, Sum
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import serializers
from dashboard.utils import (
    dashboard_login_required,
    get_common_context,
    get_theme_colors,
    seller_verified_required,
)
from registration.models import (
    User,
    NGOProfile,
    AdvertiserProfile,
    ClientProfile,
    PharmacyProfile,
    ContactPerson,
    LabProfile,
    DoctorProfile,
    HospitalProfile,
    DoctorEducation,
    DoctorSpeciality,
    DoctorExperience,
    PharmacyServices,
    PharmacyType,
    PharmacyTiming,
    LabService,
    LabFacility,
    LabTiming,
    HospitalTiming,
    AdServiceReq,
    AdvertiserType,
    ClientType,
    ClientService,
    NGOService,
)
from registration.views import (
    is_file_clean,
    validate_and_save_file,
)
from support.models import (
    IssueType,
    IssueOption,
    SupportTicket,
    FAQ,
    ChatOptionGroup,
)
from support.utils import send_custom_email
from maps.models import SearchHistory, SavedLocation
from points.models import (
    PointsActionType,
    PointsHistory,
    PointsBadge,
)
from coupon.models import Coupon, CouponClaimed
from donate.models import Donation
from ngopost.models import NGOPost

## Settings
def load_country_codes():
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'countryCodes.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
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
        'lab': handle_lab_profile,
        'hospital': handle_hospital_profile,
        'doctor': handle_doctor_profile,
    }
    handler_func = user_type_handlers.get(user.user_type)
    if handler_func:
        context.update(handler_func(user))
    context['country_codes'] = load_country_codes()
    if user.user_type == "pharmacy":
        template_name = "seller_settings/pharmacy_settings.html"
    elif user.user_type == "lab":
        template_name = "seller_settings/lab_settings.html"
    elif user.user_type == "hospital":
        template_name = "seller_settings/hospital_settings.html"
    elif user.user_type == "doctor":
        template_name = "seller_settings/doctor_settings.html"
    else:
        template_name = "settings/settings_page.html"

    return render(request, template_name, context)
    # return render(request, 'settings/settings_page.html', context)

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
        'payment_notifications': user.payment_notifications,
        'location_notification': user.location_notification,
        'quite_mode': user.quite_mode,
        'quite_mode_start_time': user.quite_mode_start_time,
        'quite_mode_end_time': user.quite_mode_end_time,
    }
    return context

def handle_contact_person(profile_type, profile):
    contact = ContactPerson.objects.filter(profile_type=profile_type, profile=profile).first()
    return {
        'contact_name': contact.name if contact else '',
        'contact_phone_country_code': contact.phone_country_code if contact else '',
        'contact_phone_number': contact.phone_number if contact else '',
        'contact_role': contact.role if contact else ''
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
    all_workingdays = PharmacyTiming.objects.filter(is_active=True)
    data = {
        'company_name': profile.company_name,
        'pharmacy_type': profile.pharmacy_type,
        'all_types': all_types,
        'services_offered': profile.services_offered,
        'all_services': all_services,
        'all_workingdays': all_workingdays,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
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
        'storefront_image_path': os.path.basename(profile.storefront_image_path) if profile.storefront_image_path else "",
    }
    data.update(handle_contact_person(user.user_type, user))
    return data

def handle_lab_profile(user):
    profile = LabProfile.objects.filter(user=user).first()
    all_timings = LabTiming.objects.filter(is_active=True)
    all_services = LabService.objects.filter(is_active=True)
    all_facilities = LabFacility.objects.filter(is_active=True)

    data = {
        'lab_name' : profile.lab_name,
        'owner_name': profile.owner_name,
        'contact_number': profile.contact_number,
        'alt_contact_number': profile.alt_contact_number,
        'lab_registration_number': profile.lab_registration_number,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'country': profile.country,
        'pincode': profile.pincode,
        'all_timings': all_timings,
        'lab_timing': profile.lab_timing,
        'services_selected': profile.services.all(),
        'all_services': all_services,
        'facilities_selected': profile.facilities.all(),
        'all_facilities': all_facilities,
        'lab_certificate_number': profile.lab_certificate_number,
        'lab_certificate_path': os.path.basename(profile.lab_certificate_path) if profile.lab_certificate_path else "",
        'identity_proof_aadhar_number': profile.identity_proof_aadhar_number,
        'identity_proof_aadhar_path': os.path.basename(profile.identity_proof_aadhar_path) if profile.identity_proof_aadhar_path else "",
        'identity_proof_pan_number': profile.identity_proof_pan_number,
        'identity_proof_pan_path': os.path.basename(profile.identity_proof_pan_path) if profile.identity_proof_pan_path else "",
        'gov_license_number': profile.gov_license_number,
        'gov_license_path': os.path.basename(profile.gov_license_path) if profile.gov_license_path else "",
        'lab_photo_path': os.path.basename(profile.lab_photo_path) if profile.lab_photo_path else "",
        'is_verified': profile.is_verified,
        'verification_status': profile.verification_status,
        'rejection_reason': profile.rejection_reason,
        'verified_at': profile.verified_at,
        'referral_code': profile.referral_code or '',
    }
    return data

def handle_hospital_profile(user):
    profile = HospitalProfile.objects.filter(user=user).first()
    data = {
        'hospital_name' : profile.hospital_name,
        'owner_name': profile.owner_name,
        'contact_no': profile.contact_no,
        'alternate_contact_no': profile.alternate_contact_no,
        'address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'pincode': profile.pincode,
        'hospital_timing': profile.hospital_timing,
        'home_visit': profile.home_visit,
        'registration_no': profile.registration_no,
        'registration_certificate_path': os.path.basename(profile.registration_certificate_path) if profile.registration_certificate_path else "",
        'aadhar_card_no': profile.aadhar_card_no,
        'aadhar_doc_path': os.path.basename(profile.aadhar_doc_path) if profile.aadhar_doc_path else "",
        'pan_card_no': profile.pan_card_no,
        'pan_doc_path': os.path.basename(profile.pan_doc_path) if profile.pan_doc_path else "",
        'hospital_logo_path': os.path.basename(profile.hospital_logo_path) if profile.hospital_logo_path else "",
        'hospital_photo_path': os.path.basename(profile.hospital_photo_path) if profile.hospital_photo_path else "",
        'phone_for_otp': profile.phone_for_otp,
        'is_verified': profile.is_verified,
        'verification_status': profile.verification_status,
        'rejection_reason': profile.rejection_reason,
        'verified_at': profile.verified_at,
        'referral_code': profile.referral_code or '',
    }
    return data

def handle_doctor_profile(user):
    profile = DoctorProfile.objects.filter(user=user).first()
    all_speciality = DoctorSpeciality.objects.filter(is_active=True)
    all_education = DoctorEducation.objects.filter(is_active=True)
    all_experience = DoctorExperience.objects.filter(is_active=True)
    data = {
        'full_name': profile.full_name,
        'gender': profile.gender,
        'age': profile.age,
        'specialty': profile.specialty,
        'all_speciality': all_speciality,
        'education': profile.education,
        'all_education': all_education,
        'experience': profile.experience,
        'all_experience': all_experience,
        'profile_photo_path': profile.profile_photo_path,
        'clinic_name': profile.clinic_name,
        'owner_name': profile.owner_name,
        'contact_number': profile.contact_number,
        'alt_contact_number': profile.alt_contact_number,
        'address': profile.full_address,
        'city': profile.city,
        'state': profile.state,
        'pincode': profile.pincode,
        'clinic_timing_from': profile.clinic_timing_from,
        'clinic_timing_to': profile.clinic_timing_to,
        'home_visit_available': profile.home_visit_available,
        'registration_number': profile.registration_number,
        'registration_certificate_path': os.path.basename(profile.registration_certificate_path) if profile.registration_certificate_path else "",
        'aadhar_number': profile.aadhar_number,
        'aadhar_doc_path': os.path.basename(profile.aadhar_doc_path) if profile.aadhar_doc_path else "",
        'pan_number': profile.pan_number,
        'pan_doc_path': os.path.basename(profile.pan_doc_path) if profile.pan_doc_path else "",
        'clinic_logo_path': os.path.basename(profile.clinic_logo_path) if profile.clinic_logo_path else "",
        'clinic_photo_path': os.path.basename(profile.clinic_photo_path) if profile.clinic_photo_path else "",
        'is_verified': profile.is_verified,
        'verification_status': profile.verification_status,
        'rejection_reason': profile.rejection_reason,
        'verified_at': profile.verified_at,
        'referral_code': profile.referral_code or '',
    }
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
    if field in ["inapp_notifications", "email_notifications", "push_notifications", "regulatory_alerts", "promotions_and_offers", "quite_mode", "payment_notifications", "location_notification"]:
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
        contact_person = ContactPerson.objects.filter(profile_type='ngo', profile=user).first()

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
                    profile=user
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
                    profile=user
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

    validate_email_phone(post_data, errors)
    required_fields = ["company_name", "city", "state", "pincode"]
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
            pharmacy_profile.pincode = post_data.get("pincode")

            pharmacy_type_value = post_data.get("pharmacy_type")
            if pharmacy_type_value:
                pharmacy_profile.pharmacy_type = get_object_or_404(PharmacyType, name=pharmacy_type_value)
            services_offered_value = post_data.get("services_offered")
            if services_offered_value:
                pharmacy_profile.services_offered = get_object_or_404(PharmacyServices, name=services_offered_value)

            pharmacy_profile.save()

            # --- Update or Create ContactPerson ---
            contact_name = post_data.get("contact_name")
            contact_phone = post_data.get("contact_phone_number")
            if contact_name or contact_phone:
                contact, _ = ContactPerson.objects.get_or_create(
                    profile_type="pharmacy",
                    profile=user
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
def update_lab_profile(request):
    post_data = request.POST
    errors = {}
    user = request.user_obj  
    
    validate_email_phone(post_data, errors)
    required_fields = ["lab_name", "city", "state", "pincode"]
    for field in required_fields:
        if not post_data.get(field):
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)
    
    try:
        with transaction.atomic():
            user.email = post_data.get('email')
            user.phone_country_code = post_data.get("countryCodes")
            user.save()
            
            lab_profile = get_object_or_404(LabProfile, user=user)
            lab_profile.save()
            
            return JsonResponse({'success': True, 'message': 'Lab profile updated successfully'})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@require_POST
@dashboard_login_required
def update_hospital_profile(request):
    post_data = request.POST
    errors = {}
    user = request.user_obj  
    validate_email_phone(post_data, errors)
    required_fields = ["hospital_name", "city", "state", "pincode"]
    for field in required_fields:
        if not post_data.get(field):
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)
    
    try:
        with transaction.atomic():
            user.email = post_data.get('email')
            user.phone_country_code = post_data.get("countryCodes")
            user.save()
            
            hospital_profile = get_object_or_404(HospitalProfile, user=user)
            hospital_profile.save()
            
            return JsonResponse({'success': True, 'message': 'Hospital profile updated successfully'})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@require_POST
@dashboard_login_required
def update_doctor_profile(request):
    post_data = request.POST
    errors = {}
    user = request.user_obj  
    validate_email_phone(post_data, errors)
    required_fields = ["clinic_name", "city", "state", "pincode"]
    for field in required_fields:
        if not post_data.get(field):
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)
    
    try:
        with transaction.atomic():
            user.email = post_data.get('email')
            user.phone_country_code = post_data.get("countryCodes")
            user.save()
            
            doctor_profile = get_object_or_404(DoctorProfile, user=user)
            doctor_profile.save()
            
            return JsonResponse({'success': True, 'message': 'Doctor profile updated successfully'})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@require_POST
@dashboard_login_required
def delete_account(request):
    user = request.user_obj
    data = json.loads(request.body)
    reason = data.get("reason", "No reason provided")

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

    elif user.user_type == 'ngo':
        NGOPost.objects.filter(user=user, saved=True).update(saved=False)

    elif user.user_type == "pharmacy":
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

#################################
## Support
#################################
@dashboard_login_required
@require_http_methods(["GET", "POST"])
def support_view(request):
    user = request.user_obj
    context = get_common_context(request, user)
    issue_types = IssueType.objects.all()
    search_query = request.GET.get('search', '').strip()

    issue_types = IssueType.objects.exclude(name='chatbot_query').all()
    tickets = SupportTicket.objects.filter(user_id=user.id).order_by('-created_at')

    if search_query:
        ticket_id_numeric = search_query.replace('#', '').strip()
        if ticket_id_numeric.isdigit():
            real_id = int(ticket_id_numeric) - 10000000
            tickets = tickets.filter(id=real_id)
        else:
            tickets = tickets.filter(
                Q(issue_option__name__icontains=search_query) |
                Q(issue_option__issue_type__name__icontains=search_query)
            )
    context.update({
        'issue_types': issue_types,
        'tickets': tickets,
    })
    return render(request, 'settings-support/support.html', context)

@dashboard_login_required
def get_issue_options(request):
    issue_type_id = request.GET.get('issue_type_id')
    options = IssueOption.objects.filter(issue_type_id=issue_type_id)
    data = [{'id': opt.id, 'name': opt.name} for opt in options]
    return JsonResponse({'options': data})

@require_POST
@dashboard_login_required
def log_custom_query(request):
    user = request.user_obj
    try:
        data = json.loads(request.body)
        query_text = data.get('query')

        if not query_text:
            return JsonResponse({'message': 'Query text is required.'}, status=400)
        
        if not user:
            return JsonResponse({'message': 'User not authenticated.'}, status=401)
        
        try:
            chatbot_issue_option = IssueOption.objects.get(
                issue_type__name='chatbot_query', 
                name='custome user query'         
            )
        except IssueOption.DoesNotExist:
            return JsonResponse(
                {'message': 'System error: Could not categorize query. Please contact direct support.'},
                status=500
            )
        except Exception as e:
            return JsonResponse(
                {'message': 'An internal error occurred while setting up the ticket.'},
                status=500
            )
        
        ticket = SupportTicket.objects.create(
            user=user,
            created_by=user, 
            issue_option=chatbot_issue_option, 
            description=query_text, 
            image=None 
        )

        return JsonResponse({
            'success': True,
            'ticket_id': ticket.ticket_id(),
            'message': 'Your query has been submitted as a ticket! We will get back to you shortly.'
        }, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid data format.'}, status=400)
    
    except Exception as e:
        return JsonResponse({'message': 'An unexpected server error occurred. Please try again.'}, status=500)
    
@require_GET
@dashboard_login_required 
def get_user_tickets(request):
    try:
        user = request.user_obj
        user_tickets = SupportTicket.objects.filter(user=user).order_by('-created_at')

        tickets_data = []
        for ticket in user_tickets:
            tickets_data.append({
                'ticket_id': ticket.ticket_id(),
                'description': ticket.description,
                'status': ticket.status,
                'issue_option_name': ticket.issue_option.name if ticket.issue_option else 'N/A',
                'created_at': ticket.created_at.isoformat(), 
                # 'last_updated_at': ticket.created_at.isoformat(),
            })

        return JsonResponse({'success': True, 'tickets': tickets_data}, safe=False, encoder=DjangoJSONEncoder)

    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Failed to retrieve tickets.'}, status=500)

@require_GET
@dashboard_login_required 
def get_bot_content_api(request):
    user = request.user_obj
    user_type = 'user'
    
    if hasattr(user, 'ngoprofile') and user.ngoprofile is not None:
        user_type = 'ngo'
    elif hasattr(user, 'advertiserprofile') and user.advertiserprofile is not None:
        user_type = 'advertiser'
    elif hasattr(user, 'clientprofile') and user.clientprofile is not None:
        user_type = 'client'
    elif hasattr(user = 'Pharmacyprofile') and user.Pharmacyprofile is not None:
        user_type = 'pharmacy'

    try:
        chat_group = ChatOptionGroup.objects.get(user_type=user_type, is_active=True)
        return JsonResponse(chat_group.options_data)

    except ChatOptionGroup.DoesNotExist:
        try:
            user_group = ChatOptionGroup.objects.get(user_type='user', is_active=True)
            fallback_data = user_group.options_data.copy()
            if user_type != 'user': 
                fallback_data["initial_message"] = f"No specific content found for your type ({user_type}). " + fallback_data.get("initial_message", "Here's some general information:")
            return JsonResponse(fallback_data, status=200) 

        except ChatOptionGroup.DoesNotExist:
            return JsonResponse(
                {"initial_message": "Sorry, chatbot content is not configured. Please contact support."},
                status=500 
            )

    except Exception as e:
        return JsonResponse({"initial_message": "Sorry, an unexpected error occurred. Please try again later."},status=500)

@dashboard_login_required 
def submit_support_ticket(request):
    user = request.user_obj

    if request.method == 'POST':
        issue_type_id = request.POST.get('issue_type')
        issue_option_id = request.POST.get('select_issue')
        description = request.POST.get('description')
        image_file = request.FILES.get('image')
        
        image_path = None
        if image_file:
            image_path, error = validate_and_save_file(
                image_file,
                subdir='support_issues',
                field_label='Support Ticket Image',
                user_type='user'
            )
            if error:
                return JsonResponse({'success': False, 'message': error}, status=400)

        if issue_type_id and issue_option_id:
            try:
                issue_option = IssueOption.objects.get(id=issue_option_id, issue_type_id=issue_type_id)
                ticket = SupportTicket.objects.create(
                    user=user,
                    created_by=user,
                    issue_option=issue_option,
                    description=description,
                    image=image_path,
                )
                return JsonResponse({'success': True, 'ticket_id': ticket.ticket_id(), 'message': 'Ticket created successfully.'})
            except IssueOption.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid issue type or option'}, status=400)

        return JsonResponse({'success': False, 'message': 'Missing issue type or option'}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@dashboard_login_required
def get_ticket_lists(request):
    user = request.user_obj
    user_type = user.user_type
    tickets = SupportTicket.objects.select_related(
        'issue_option__issue_type'
    ).filter(
        user__user_type=user_type,  
        user=user  
    ).order_by('-id')

    ticket_list = []

    for ticket in tickets:
        ticket_list.append({
            "ticket_id": ticket.ticket_id(),
            "date_time": ticket.created_at.strftime("%d/%m/%Y, %H:%M"),
            "issue_type": ticket.issue_option.issue_type.name if ticket.issue_option else "N/A",
            "status": ticket.get_status_display(),
            "status_class": get_status_class(str(ticket.status)),
        })

    return JsonResponse(ticket_list, safe=False)

@dashboard_login_required
def filter_support_tickets(request):
    status = request.GET.get('status')
    issue_type = request.GET.get('issue_type')
    tickets = SupportTicket.objects.all()

    if status:
        tickets = tickets.filter(status=status)
    if issue_type:
        tickets = tickets.filter(issue_option__issue_type__name=issue_type)

    data = serializers.serialize("json", tickets.select_related("issue_option", "user"))
    return JsonResponse({"tickets": data})

def get_status_class(status_id):
    return {
        '1': 'bg-light-gray text-dark-gray',
        '2': 'bg-peach text-burnt-orange',
        '3': 'bg-dark-gray text-light-gray',
        '4': 'bg-mint-cream text-green',
        '5': 'bg-light-red text-dark-red',
        '6': 'bg-pale-red text-dark-red',
    }.get(status_id, 'badge-light')
    
@dashboard_login_required
def ticket_details(request):
    user = request.user_obj
    email = user.email
    usertype = user.user_type
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            ticket_id = data.get("ticket_id", "")

            db_id = int(ticket_id.replace("#", "")) - 10000000

            ticket = SupportTicket.objects.select_related(
                "issue_option__issue_type", "created_by"
            ).get(id=db_id)
            
            created_at = ticket.created_at.strftime("%d/%m/%Y, %I:%M %p")  
            updated_at = ticket.updated_at.strftime("%d/%m/%Y, %I:%M %p")  

            return JsonResponse({
                "ticket_id": ticket.ticket_id(),
                "email": email,
                "usertype": usertype,
                "created_at": created_at,
                "updated_at": updated_at,
                "issue_type": ticket.issue_option.issue_type.name if ticket.issue_option else "N/A",
                "status": ticket.get_status_display(),
                "description": ticket.description,
                "img": ticket.image if ticket.image else "",
            })

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request method"})

@dashboard_login_required
def filter_tickets(request):
    if request.method == "POST":
        data = json.loads(request.body)
        from_date_str = data.get("from_date")
        to_date_str = data.get("to_date")

        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = (
                datetime.strptime(to_date_str, "%Y-%m-%d").date()
                if to_date_str else None
            )
        except Exception:
            return JsonResponse({"error": "Invalid date format"})

        if to_date:
            tickets = SupportTicket.objects.filter(
                created_at__date__gte=from_date,
                created_at__date__lte=to_date
            ).order_by("-created_at")
        else:
            tickets = SupportTicket.objects.filter(
                created_at__date=from_date
            ).order_by("-created_at")

        results = [
            {
                "ticket_id": ticket.ticket_id(),
                "date_time": ticket.created_at.strftime("%d/%m/%Y, %H:%M"),
                "issue_type": ticket.issue_option.issue_type.name if ticket.issue_option else "N/A",
                "status": ticket.get_status_display(),
                "status_class": get_status_class(ticket.status),
            }
            for ticket in tickets
        ]

        return JsonResponse({"tickets": results})

    return JsonResponse({"error": "Invalid method"})

def filter_tickets_old(request):
    if request.method == "POST":
        data = json.loads(request.body)
        from_date_str = data.get("from_date")
        to_date_str = data.get("to_date")

        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        except Exception:
            return JsonResponse({"error": "Invalid date format"})

        tickets = SupportTicket.objects.filter(
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
        ).order_by("-created_at")

        results = [
            {
                "ticket_id": ticket.ticket_id(),
                "date_time": ticket.created_at.strftime("%d/%m/%Y, %H:%M"),
                "issue_type": ticket.issue_option.issue_type.name if ticket.issue_option else "N/A",
                "status": ticket.get_status_display(),
                "status_class": get_status_class(ticket.status),
            }
            for ticket in tickets
        ]

        return JsonResponse({"tickets": results})

    return JsonResponse({"error": "Invalid method"})

@dashboard_login_required
def faq_lists(request):
    user = request.user_obj
    query = request.GET.get('search', '').strip()

    if query:
        faqs = FAQ.objects.filter(
            Q(question__icontains=query) | Q(answer__icontains=query),
            user=user
        )
    else:
       faqs = FAQ.objects.filter(user=user)

    return render(request, 'settings-support/support-faq.html', {'faqs': faqs})

def faq_lists_old(request):
    query = request.GET.get('search', '').strip()

    if query:
        faqs = FAQ.objects.filter(
            Q(question__icontains=query) | Q(answer__icontains=query)
        )
    else:
        faqs = FAQ.objects.all()

    return render(request, 'settings-support/support-faq.html', {'faqs': faqs})

def send_support_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        description = request.POST.get('description')

        if not email or not description:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        try:
            context = {
                'email': email,
                'description': description,
            }

            send_custom_email(
                to_email='laxmi.kumari@aibuzz.net',
                subject=f"Support Request from {email}",
                template_name='settings-support/emails/email-template.html',
                context=context,
                from_email=email
            )

            return JsonResponse({'message': 'Email sent successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


## Donate

@dashboard_login_required
@require_GET
def donate_view(request):
    user = request.user_obj
    if user.user_type == 'advertiser':
        user_profile = AdvertiserProfile.objects.filter(user=user).first()
    elif user.user_type == 'client':
        user_profile = ClientProfile.objects.filter(user=user).first()
    elif user.user_type == 'pharmacy':
        user_profile = PharmacyProfile.objects.filter(user=user).first()
    elif user.user_type == 'lab':
        user_profile = LabProfile.objects.filter(user=user).first()
    elif user.user_type == 'doctor':
        user_profile = DoctorProfile.objects.filter(user=user).first()
    elif user.user_type == 'hospital':
        user_profile = HospitalProfile.objects.filter(user=user).first()

    donation_query = request.GET.get('donation_query', '').strip().lower()

    donations = Donation.objects.filter(user=request.user_obj).select_related('ngopost', 'ngopost__user', 'ngopost__user__ngoprofile', 'ngopost__post_type')
    if donation_query:
        donations = [d for d in donations if
                     donation_query in (d.ngopost.post_type.name.lower() if d.ngopost and d.ngopost.post_type else '') or
                     donation_query in (d.ngopost.user.ngoprofile.ngo_name.lower() if d.ngopost and d.ngopost.user and hasattr(d.ngopost.user, 'ngoprofile') and d.ngopost.user.ngoprofile.ngo_name else '')]
    context = get_common_context(request, request.user_obj)
    color_hex_map = {
        "living-coral": "#FF6F61",
        "dark-blue": "#123456",
        "violet-sky": "#6B79F5",
        "light-sea-green": "#3AAFA9",
    }
    primary_bg = context.get("primary_bg")
    context["hexcolor"] = color_hex_map.get(primary_bg)
    if user.user_type == "lab":
        context.update({
        "donations": donations,
        "donation_query": donation_query,
        'user_display_name': user_profile.lab_name,
    })
    elif user.user_type == "doctor":
        context.update({
            "donations": donations,
            "donation_query": donation_query,
            'user_display_name': user_profile.clinic_name,
        })
    elif user.user_type == "hospital":
        context.update({
            "donations": donations,
            "donation_query": donation_query,
            'user_display_name': user_profile.hospital_name,
        })
    else:
        context.update({
            "donations": donations,
            "donation_query": donation_query,
            'user_display_name': user_profile.company_name,
        })
    return render(request, "donate/donate.html", context)

@dashboard_login_required
@require_GET
def get_organization_posts(request):
    user = request.user_obj
    query = request.GET.get("query", "").strip()
    start = request.GET.get("start_date", "").strip()
    end = request.GET.get("end_date", "").strip()
    daterange = request.GET.get("daterange", "").strip().lower()
    page = int(request.GET.get("page", 1))

    filters = Q(end_date__gte=timezone.now().date())

    if query:
        filters &= (
            Q(header__icontains=query) |
            Q(city__name__icontains=query) |
            Q(state__name__icontains=query) |
            Q(country__name__icontains=query) |
            Q(post_type__name__icontains=query) |
            Q(user__ngoprofile__ngo_name__icontains=query)
        )

    now = timezone.now()
    applied_date_filter = None

    if daterange == "1 week":
        filters &= Q(created_at__date__gte=now.date() - timedelta(days=7))
        applied_date_filter = "Last 1 Week"

    elif daterange == "1 month":
        filters &= Q(created_at__date__gte=now.date() - timedelta(days=30))
        applied_date_filter = "Last 1 Month"

    elif daterange == "1 year":
        filters &= Q(created_at__date__gte=now.date() - timedelta(days=365))
        applied_date_filter = "Last 1 Year"

    if start and end:
        start_date = parse_date(start)
        end_date = parse_date(end)
        if start_date and end_date:
            filters &= Q(created_at__date__range=(start_date, end_date))
            applied_date_filter = f"Explicit Range: {start_date} → {end_date}"

    posts = NGOPost.objects.filter(filters).select_related("user").order_by("-created_at")

    paginator = Paginator(posts, 6)
    posts_page = paginator.get_page(page)

    user_ids = [post.user_id for post in posts_page]
    profiles = NGOProfile.objects.filter(user_id__in=user_ids)
    profile_map = {p.user_id: p for p in profiles}

    for post in posts_page:
        profile = profile_map.get(post.user_id)
        post.ngo_name = profile.ngo_name if profile else "NGO Name Not Found"
        post.website_url = profile.website_url if profile else ""

    html = render_to_string(
        "donate/partials/organization-cards.html",
        {"ngo_posts": posts_page,
        **get_common_context(request, user)},
        request=request,
    )

    return JsonResponse({
        "html": html,
        "current_page": posts_page.number,
        "total_pages": paginator.num_pages,
    })

@dashboard_login_required
def donate_pay_view(request, post_id=None):
    post = None
    ngo_profile = None
    user = request.user_obj
    context = get_common_context(request, user)
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

        if (post.donation_received or Decimal('0.00')) + Decimal(str(amount)) > post.target_donation:
            return JsonResponse({'error': 'Donation exceeds the target amount for this post.'}, status=400)
        
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
        if not pan_number or len(pan_number) != 10:
            return JsonResponse({'error': 'Invalid PAN number'}, status=400)
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
            PointsHistory.objects.create(user=user, action_type=action_type_obj, points=action_type_obj.default_points)
        except PointsActionType.DoesNotExist:
            print("PointsActionType for 'Donate' does not exist. No points awarded.")
        return JsonResponse({'success': True, 'order_id': order_id, 'transaction_id': transaction_id})
    context.update({ "post": post, "ngo_profile": ngo_profile})
    return render(request, "donate/donate-pay.html", context)

@dashboard_login_required
@require_GET
def get_donation_history(request):
    user = request.user_obj

    query = request.GET.get('query', '').strip()
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    date_range = request.GET.get('daterange', '').strip().lower()
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

        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            filters &= Q(created_at__range=(start_date, end_date))
        except Exception:
            pass  

    donations = Donation.objects.filter(filters).order_by('-created_at')
    paginator = Paginator(donations, limit)
    page_obj = paginator.get_page(page)
    
    html = render_to_string("donate/partials/donation-history.html", {
        "donation_history": page_obj.object_list,
        'today': date.today(),
        **get_common_context(request, request.user_obj),
    })
    return JsonResponse({
        "html": html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,
    })

@dashboard_login_required    
def get_donate_bill(request, donation_id):
    user = request.user_obj
    donation = Donation.objects.select_related('ngopost__user__ngoprofile').get(id=donation_id)
    
    ngo_user = donation.ngopost.user
    ngo_profile = NGOProfile.objects.filter(user=ngo_user).first()
    contact_person = ContactPerson.objects.filter(
        profile_type=user.user_type,
        profile=user
    ).first()  


    response_data = {
        "receipt_no": donation.id,
        "payment_date": donation.payment_date.strftime("%d-%b-%Y"),
        "ngo_name": ngo_profile.ngo_name,
        "pan": ngo_profile.pan_number,
        "amount": f"₹{donation.amount}",
        "pay_mode": f"{donation.payment_method}",
        "address": f"{ngo_profile.address}, {ngo_profile.city}, {ngo_profile.state}, {ngo_profile.pincode}",
        "name": contact_person.name if contact_person else "",
        "email": user.email if user.email else "",
    }

    return JsonResponse(response_data)

@dashboard_login_required    
def get_platform_bill(request, donation_id):
    user = request.user_obj
    donation = Donation.objects.select_related('ngopost__user__ngoprofile').get(id=donation_id)
    
    ngo_user = donation.ngopost.user
    ngo_profile = NGOProfile.objects.filter(user=ngo_user).first()
    contact_person = ContactPerson.objects.filter(
        profile_type=user.user_type,
        profile=user
    ).first()


    response_data = {
        "receipt_no": donation.id,
        "payment_date": donation.payment_date.strftime("%d-%b-%Y"),
        "ngo_name": ngo_profile.ngo_name,
        "pan": ngo_profile.pan_number,
        "gst": donation.gst,
        "amount": f"₹{donation.amount}",
        "pay_mode": f"₹{donation.payment_method}",
        "address": f"{ngo_profile.address}, {ngo_profile.city}, {ngo_profile.state}, {ngo_profile.pincode}",
        "name": contact_person.name if contact_person else "",
        "email": user.email if user.email else "",
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

        return JsonResponse({'success': True, 'saved': donation.saved, 'text_class': get_theme_colors(request.user_obj.user_type).get("text", "blue-500")})

    except Donation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Donation not found'}, status=404)

@dashboard_login_required
@require_GET
def export_donation_history(request):
    user = request.user_obj
    # date_range = request.GET.get('daterange', '').strip().lower()
    filters = Q(user=user)
    donations = Donation.objects.filter(filters).order_by('-created_at')
    html = render_to_string("donate/partials/export-donate-history.html", {
        "donation_history": donations,
        'today': date.today(),
    })
    return JsonResponse({
        "html": html,
        "total_items": donations.count(),  # Add this
    })


## Rewards

@dashboard_login_required
def points_dashboard(request):
    user = request.user_obj

    context = get_common_context(request, user)

    # Extra data for chart only
    chart_action_types = context.get("chart_action_types", [])
    chart_data = defaultdict(lambda: [0] * 7)
    today = datetime.date.today()
    last_7_days = [today - datetime.timedelta(days=6 - i) for i in range(7)]

    for day_index, day in enumerate(last_7_days):
        for action_type in chart_action_types:
            action_obj = PointsActionType.objects.filter(
                action_type__iexact=action_type
            ).first()
            if action_obj:
                points = (
                    PointsHistory.objects.filter(
                        user=user, action_type=action_obj, timestamp__date=day
                    ).aggregate(total=Sum("points"))["total"]
                    or 0
                )
                chart_data[action_type.title()][day_index] = points

    context.update(
        {
            "chart_labels": [d.strftime("%d/%m") for d in last_7_days],
            "chart_data": dict(chart_data),
            "all_badges": PointsBadge.objects.all(),
        }
    )
    print(context)
    return render(request, "rewards/rewards.html", context)

@dashboard_login_required
def get_coupon_data(request, is_popular=False):
    user = request.user_obj
    try:
        query = request.GET.get('search', '').strip().lower()
        date_range = request.GET.get('daterange', '').strip().lower()
        start_date_str = request.GET.get('start_date', '').strip()
        end_date_str = request.GET.get('end_date', '').strip()
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 4))  # default 4 per page

        now = timezone.now()
        coupons = Coupon.objects.select_related('category', 'brand_name')

        if query:
            coupons = coupons.filter(
                Q(title__icontains=query) |
                Q(code__icontains=query) |
                Q(category__name__icontains=query) |
                Q(brand_name__name__icontains=query)
            )

        if date_range == "1 week":
            coupons = coupons.filter(created_at__gte=now - datetime.timedelta(weeks=1))
        elif date_range == "1 month":
            coupons = coupons.filter(created_at__gte=now - datetime.timedelta(days=30))
        elif date_range == "1 year":
            coupons = coupons.filter(created_at__gte=now - datetime.timedelta(days=365))
        elif start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + datetime.timedelta(days=1)
                coupons = coupons.filter(created_at__range=(start_date, end_date))
            except ValueError:
                return JsonResponse({"html": "", "error": "Invalid date format."})

        if is_popular:
            coupons = coupons.order_by('-redeemed_count')
        else:
            coupons = coupons.order_by('-created_at')

        paginator = Paginator(coupons, limit)
        page_obj = paginator.get_page(page)

        data_list = []
        for c in page_obj:
            redeemed = c.redeemed_count or 0
            max_redemptions = c.max_redemptions or 100
            item = {
                "title": c.title[:20] if is_popular else c.title,
                "id": c.id,
                "description": c.description[:120] if is_popular else c.description,
                "category": c.category.name if c.category else "N/A",
                "brand_name": c.brand_name.name if c.brand_name else "N/A",
                "code": c.code,
                "redeemed_count": redeemed,
                "max_redemptions": max_redemptions,
            }
            if is_popular:
                item["percent_used"] = int((redeemed / max_redemptions) * 100)
            data_list.append(item)

        context = {"coupons" if is_popular else "products": data_list}
        context.update(get_common_context(request, user))
        html = render_to_string(
            "rewards/partials/coupon_card_layout.html" if is_popular else "rewards/partials/coupon_cards.html",
            context
        )

        return JsonResponse({
            "html": html,
            "pagination": {
                "page": page_obj.number,
                "num_pages": paginator.num_pages
            }
        })

    except Exception as e:
        return JsonResponse({"html": "", "error": str(e)})

@require_GET
def get_coupon_cards(request):
    return get_coupon_data(request, is_popular=False)

@require_GET
def get_popular_coupon_cards(request):
    return get_coupon_data(request, is_popular=True)

@require_GET
def points_history_view(request):
    context = filter_points(request)
    return render(request, 'rewards/partials/points_table.html', context)

@require_GET
def ajax_filtered_points(request):
    context = filter_points(request)
    return render(request, 'rewards/partials/points_table.html', context)

@dashboard_login_required
def filter_points(request):
    user = request.user_obj
    today = timezone.now().date()

    search_query = request.GET.get('search', '').strip().lower()
    date_filter = request.GET.get('date_filter', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    page = request.GET.get('page', 1)
    # Base queryset
    history_queryset = PointsHistory.objects.filter(user=user).select_related('action_type')

    # Apply date filtering
    if date_filter == 'last_week':
        last_week = today - datetime.timedelta(days=7)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_week)
    elif date_filter == 'last_month':
        last_month = today - datetime.timedelta(days=30)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_month)
    elif date_filter == 'last_year':
        last_year = today - datetime.timedelta(days=365)
        history_queryset = history_queryset.filter(timestamp__date__gte=last_year)
    elif date_filter == 'custom' and start_date and end_date:
        try:
            start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            history_queryset = history_queryset.filter(timestamp__date__range=(start_dt, end_dt))
        except ValueError:
            pass  # invalid date inputs are ignored

    # Search filtering
    if search_query:
        history_queryset = history_queryset.filter(
            Q(action_type__action_type__icontains=search_query)
        )

    history_queryset = history_queryset.order_by('-timestamp')

    # Pagination
    paginator = Paginator(history_queryset, 5)  # 10 items per page
    page_obj = paginator.get_page(page)

    history_data = [
        {
            'timestamp': h.timestamp.strftime('%d/%m/%y, %H:%M'),
            'action_type': h.action_type.action_type.title() if h.action_type else 'Unknown',
            'points': h.points,
            'status': 'Completed'
        }
        for h in page_obj
    ]

    return {
        'data': history_data,
        'page_obj': page_obj,
        **get_common_context(request, user)
    }

@require_POST
@dashboard_login_required
def claim_coupon(request):
    try:
        data = json.loads(request.body)
        coupon_id = data.get('coupon_id')
        coupon = Coupon.objects.get(id=coupon_id)
        user = request.user_obj

        if CouponClaimed.objects.filter(user=user, coupon=coupon).exists():
            return JsonResponse({'status': 'already_claimed'})

        CouponClaimed.objects.create(
            user=user,
            coupon=coupon,
            expiry_date=coupon.validity
        )
        return JsonResponse({'status': 'success'})

    except Coupon.DoesNotExist:
        return JsonResponse({'status': 'coupon_not_found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@dashboard_login_required
def get_claimed_coupons(request):
    try:
        user = request.user_obj
        search = request.GET.get('search', '').strip()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        date_range = request.GET.get('date_range', '').lower()
        page = request.GET.get('page', 1)

        claimed_qs = CouponClaimed.objects.filter(user=user).select_related(
            'coupon__category', 'coupon__brand_name'
        )

        # Search
        if search:
            claimed_qs = claimed_qs.filter(
                Q(coupon__title__icontains=search) |
                Q(coupon__code__icontains=search) |
                Q(coupon__category__name__icontains=search) |
                Q(coupon__brand_name__name__icontains=search)
            )

        # Normalize date_range
        if date_range:
            date_range = date_range.strip().lower()
            today = timezone.now().date()

            if date_range == "1 week":
                claimed_qs = claimed_qs.filter(date_claimed__date__gte=today - datetime.timedelta(weeks=1))
            elif date_range == "1 month":
                claimed_qs = claimed_qs.filter(date_claimed__date__gte=today - datetime.timedelta(days=30))
            elif date_range == "1 year":
                claimed_qs = claimed_qs.filter(date_claimed__date__gte=today - datetime.timedelta(days=365))


        # Start Date Filter
        if start_date:
            try:
                start = parse_date(start_date)
                if start:
                    claimed_qs = claimed_qs.filter(date_claimed__date__gte=start)
            except Exception as e: 
                return JsonResponse({"error": f"Error occurred - Invalid start date: {str(e)}"}, status=500)

        # End Date Filter
        if end_date:
            try:
                end = parse_date(end_date)
                if end:
                    claimed_qs = claimed_qs.filter(date_claimed__date__lte=end)
            except Exception as e:
                return JsonResponse({"error": f"Error occurred - Invalid end date: {str(e)}"}, status=500)

        paginator = Paginator(claimed_qs.order_by('-date_claimed'), 5)
        try:
            page_obj = paginator.get_page(page)
        except Exception:
            page_obj = paginator.page(1)

        html = render_to_string("rewards/partials/coupon_claimed_table.html", {
            "claimed_coupons": page_obj
        })

        pagination_html = render_to_string("rewards/partials/coupon_claimed_pagination.html", {
            "page_obj": page_obj,
            **get_common_context(request, user)
        })

        return JsonResponse({"html": html, "pagination": pagination_html})
    
    except Exception as e:
        return JsonResponse({"error": f"Error occurred: {str(e)}"}, status=500)

