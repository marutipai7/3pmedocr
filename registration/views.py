import os
import re
import asyncio
import pyotp
from .models import *
from .email_otp import async_send_otp_email, send_forgot_password_email
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

ROLE_TO_TEMPLATE = {
    "login": "login/login.html",
    "customer": "registration/register_user.html",
    "ngoOwner": "registration/ngo_register.html",
    "Pharmacy": "registration/pharmacy_register.html",
    "client": "registration/client_register.html",
    "advertiser": "registration/advertiser_register.html",
    'lab': "registration/lab_register.html",
    'hospital': "registration/hospital_register.html",
    'doctor': "registration/doctor_register.html",
}

@require_POST
def send_otp(request):
    email = request.POST.get("email")
    if not email:
        return JsonResponse({"success": False, "message": "Please enter email"}, status=400)
    try:
        validate_email(email)
    except:
        return JsonResponse({"success": False, "message": "Invalid email address"}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "This email is already registered."}, status=400)

    # Generate secret + OTP
    token_data = async_to_sync(async_send_otp_email)(type("obj", (object,), {"email": email}))
    secret = token_data["otp_token"]

    # Cache secret (NOT otp value) for 5 minutes
    cache.set(f"otp:{secret}", {
        "email": email,
        "secret": secret,
        "created_at": timezone.now().isoformat()
    }, timeout=300)

    return JsonResponse({"success": True, "token": secret, "message": "OTP sent successfully"})

@require_POST
def verify_otp(request):
    bearer_token = request.POST.get("token")
    otp = request.POST.get("otp")

    if not bearer_token or not otp:
        return JsonResponse({"success": False, "message": "Missing token or OTP"}, status=400)

    cache_key = f"otp:{bearer_token}"
    otp_data = cache.get(cache_key)
    if not otp_data:
        return JsonResponse({"success": False, "message": "OTP expired or invalid"}, status=400)
    
    if bearer_token != otp_data.get("secret"):
        return JsonResponse({"success": False, "message": "Invalid or forged token"}, status=400)

    secret = otp_data["secret"]
    totp = pyotp.TOTP(secret, interval=300)  # must match send_otp.py
    if not totp.verify(otp, valid_window=1):
        return JsonResponse({"success": False, "message": "Invalid OTP"}, status=400)

    return JsonResponse({"success": True, "message": "OTP verified successfully"})

def welcome(request):
    return render(request, 'registration/welcome.html')

def register_by_role(request, role):
    tpl = ROLE_TO_TEMPLATE.get(role)
    if not tpl:
        tpl = "registration/welcome.html"

    context = {}

    if role == "client":
        context["client_types"] = ClientType.objects.filter(is_active=True)
        context["client_services"] = ClientService.objects.filter(is_active=True)

    elif role == "advertiser":
        context["advertiser_types"] = AdvertiserType.objects.filter(is_active=True)
        context["ad_service_reqs"] = AdServiceReq.objects.filter(is_active=True)

    elif role == "ngoOwner":
        context["ngo_services"] = NGOService.objects.filter(is_active=True)

    elif role == "Pharmacy":
        context["pharmacy_types"] = PharmacyType.objects.filter(is_active=True)
        context["pharmacy_services"] = PharmacyServices.objects.filter(is_active=True)
        context["pharmacy_timing"] = PharmacyTiming.objects.filter(is_active=True)
    
    elif role == "lab":
        context["lab_services"] = LabService.objects.filter(is_active=True)
        context["lab_facilities"] = LabFacility.objects.filter(is_active=True)
        context["lab_timing"] = LabTiming.objects.filter(is_active=True)

    elif role == "doctor":
        context["doctor_speciality"] = DoctorSpeciality.objects.filter(is_active=True)
        context["doctor_experience"] = DoctorExperience.objects.filter(is_active=True)
        context["doctor_education"] = DoctorEducation.objects.filter(is_active=True)

    return render(request, tpl, context)

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def is_file_clean(file_obj):
    return True

def validate_and_save_file(file_obj, subdir, field_label, user_type='common'):
    if not file_obj:
        return '', f"{field_label} is required. (Validation failed)"
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return '', f"{field_label} must be a PDF or image file."
    if file_obj.size > MAX_FILE_SIZE:
        return '', f"{field_label} must be under 5MB."
    if not is_file_clean(file_obj):
        return '', f"{field_label} failed virus scan."

    upload_dir = os.path.join(f"{user_type}_docs", subdir)
    os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_dir), exist_ok=True)
    filename = default_storage.save(os.path.join(upload_dir, file_obj.name), file_obj)
    return filename, None 

def login_page(request):
    return render(request, 'login/login.html')

@csrf_protect
@require_POST
def login_auth(request):
    data = request.POST
    email = data.get("email").strip()
    password = data.get("password").strip()
    remember_me = data.get("remember_me")
    errors = {}

    if not email:
        errors["email"] = "Email is required."
    if not password:
        errors["password"] = "Password is required."
    if errors:
        return JsonResponse({"success": False, "errors": errors})

    try:
        user = User.objects.get(email=email)
        if not check_password(password, user.password):
            errors["password"] = "Invalid email or password."
            return JsonResponse({"success": False, "errors": errors})
        
        if not user.is_active:
            errors["account"] = "Your account is deleted. Please contact support."
            return JsonResponse({"success": False, "errors": errors})
        
        # Update last_login here
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        
        request.session['user_id'] = user.id
        if remember_me:
            request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            request.session.set_expiry(0)
        dashboard_url = reverse("dashboard")
        logger.info(f"User {user.email} logged in successfully. Redirecting to {dashboard_url}")
        logger.info(f"User ID: {user.id}, Email: {user.email}, User Type: {user.user_type}")
        return JsonResponse({"success": True, "redirect": dashboard_url})
    except User.DoesNotExist:
        errors["password"] = "Invalid email or password."
        return JsonResponse({"success": False, "errors": errors})

@csrf_protect
@require_POST
def save_user(request):
    data = request.POST
    errors = {}
    # Email
    email = data.get("email")
    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."
        if User.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."
            
    otp_token = data.get("otp_token")
    if not otp_token:
        errors["otp1"] = "Please refresh the page."
    email_otp = data.get("otp1")  # from HTML field "otp1"
    if not email_otp:
        errors["otp1"] = "OTP is required."
    otp_verification = verify_otp(email, email_otp, otp_token)
    if not otp_verification["success"]:
        errors["otp1"] = otp_verification["message"]

    # Password
    password = data.get("password")
    if not password or len(password) < 8:
        errors["password"] = "Password is required (min 8 chars)."

    # Phone
    phone_number = data.get("phone_number")
    if not phone_number or not re.match(r"^\d{10}$", phone_number):
        errors["phone_number"] = "Enter a valid phone number (10 digits)."

    # Name
    name = data.get("name")
    if not name:
        errors["name"] = "Name is required."

    # DOB (optional, but check format if provided)
    dob = data.get("dob")
    if dob and not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
        errors["dob"] = "Enter a valid date (YYYY-MM-DD)."

    # Gender (optional, but check if provided)
    gender = data.get("gender")
    if gender and gender not in ("male", "female", "other"):
        errors["gender"] = "Select a valid gender."

    address = data.get("address")
    if not address:
        errors["address"] = "Address is required."
    city = data.get("city")
    if not city:
        errors["city"] = "City/District is required."
    state = data.get("state")
    if not state:
        errors["state"] = "State is required."
    pincode = data.get("pincode")
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter a valid pincode."
    country = data.get("country")
    if not country:
        errors["country"] = "Country is required."

    referral_code = data.get("referral_code")
    phone_country_code = data.get("phone_country_code", "+91")

    # If any errors, return as JSON
    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    user = User.objects.create(
        email=email,
        phone_country_code=phone_country_code,
        phone_number=phone_number,
        password=make_password(password),
        user_type="user"
    )

    UserProfile.objects.create(
        user=user,
        name=name,
        dob=dob or None,
        gender=gender,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        country=country,
        referral_code=referral_code,
        otp=email_otp,
    )
    return JsonResponse({"success": True, "message": "User registered successfully."})

@csrf_protect
@require_POST
def save_ngo(request):
    data = request.POST
    files = request.FILES
    errors = {}

    # --- Validation ---
    email = data.get("email")
    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."
        if User.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."

    password = data.get("password")
    confirm_password = data.get("confirm_password")
    if not password or len(password) < 8:
        errors["password"] = "Password is required (min 8 chars)."
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."
        
    otp_token = data.get("otp_token")
    email_otp = data.get("otp1")
    # if not email_otp:
    #     errors["otp1"] = "OTP is required."
    # otp_verification = verify_otp(email, email_otp, otp_token)
    # if not otp_verification["success"]:
    #     errors["otp1"] = otp_verification["message"]
    
    # Phone and country code
    phone_country_code = "+91"  # default; 
    phone_number = data.get("phone_number1")
    if not phone_number or not re.match(r"^\d{10}$", phone_number):
        errors["phone_number1"] = "Enter a valid phone number (10 digits)."

    ngo_name = data.get("ngo_name")
    if not ngo_name:
        errors["ngo_name"] = "NGO Name is required."

    website_url = data.get("website_url")
    ngo_service_id = data.get("ngo_service")
    ngo_service = None
    if ngo_service_id:
        try:
            ngo_service = NGOService.objects.get(name=ngo_service_id)
        except Exception as e:
            errors["ngo_service"] = "Invalid NGO service selected."

    address = data.get("address")
    if not address:
        errors["address"] = "Address is required."
    city = data.get("dist")
    if not city:
        errors["dist"] = "City/District is required."
    state = data.get("state")
    if not state:
        errors["state"] = "State is required."
    pincode = data.get("pincode")
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter a valid pincode."
    country = data.get("country")
    if not country:
        errors["country"] = "Country is required."

    ngo_registration_number = data.get("ngo_registration_number")
    if not ngo_registration_number:
        errors["ngo_registration_number"] = "Registration number is required."
    ngo_registration_doc_path, err = validate_and_save_file(
        files.get("ngo_registration_doc"), "registration", "Registration Document", user_type="ngo")
    if not ngo_registration_doc_path:
        errors["ngo_registration_doc"] = "Registration document is required if registration number is provided."
    if err:
        errors["ngo_registration_doc"] = err

    pan_number = data.get("pan_number")
    if not pan_number:
        errors["pan_number"] = "PAN number is required."
    pan_doc_path, err = validate_and_save_file(
        files.get("pan_doc"), "pan", "PAN Document",user_type="ngo")
    if not pan_doc_path:
        errors["pan_doc"] = "PAN document is required if PAN number is provided."
    if err:
        errors["pan_doc"] = err

    gst_number = data.get("gst_number")
    if not gst_number:
        errors["gst_number"] = "GST number is required."
    gst_doc_path, err = validate_and_save_file(
        files.get("gst_doc"), "gst", "GST Document", user_type="ngo")
    if not gst_doc_path:
        errors["gst_doc"] = "GST document is required if GST number is provided."
    if err:
        errors["gst_doc"] = err

    tan_number = data.get("tan_number")
    if not tan_number:
        errors["tan_number"] = "TAN number is required."
    tan_doc_path, err = validate_and_save_file(
        files.get("tan_doc"), "tan", "TAN Document", user_type="ngo")
    if not tan_doc_path:
        errors["tan_doc"] = "TAN document is required if TAN number is provided."
    if err:
        errors["tan_doc"] = err

    section8_number = data.get("section8_number")
    if not section8_number:
        errors["section8_number"] = "Section 8 number is required."
    section8_doc_path, err = validate_and_save_file(
        files.get("section8_doc"), "section8", "Section 8 Document", user_type="ngo")
    if not section8_doc_path:
        errors["section8_doc"] = "Section 8 document is required if number is provided."
    if err:
        errors["section8_doc"] = err

    doc_12a_number = data.get("doc_12a_number")
    if not doc_12a_number:
        errors["doc_12a_number"] = "12A number is required."
    doc_12a_path, err = validate_and_save_file(
        files.get("doc_12a"), "doc_12a", "12A Document", user_type="ngo")
    if not doc_12a_path:
        errors["doc_12a"] = "12A document is required if number is provided."
    if err:
        errors["doc_12a"] = err

    brand_image_path, err = validate_and_save_file(
        files.get("brand_image"), "brand_image", "Brand Image", user_type="ngo")
    if not brand_image_path:
        errors["brand_image"] = "Brand image is required if selected."
    if brand_image_path and err:
        errors["brand_image"] = err

    brand_description = data.get("brand_description")
    referral_code = data.get("referral_code")
    contact_person_name = data.get("contact_person_name")
    contact_person_phone = data.get("contact_person_phone")
    contact_person_role = data.get("contact_person_role")
    contact_person_otp = data.get("otp2")
    
    if not contact_person_name:
        errors["contact_person_name"] = "Contact person name is required."
    if not contact_person_phone:
        errors["contact_person_phone"] = "Contact person phone is required."
    if not contact_person_role:
        errors["contact_person_role"] = "Contact person role is required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # --- Save User & NGOProfile ---
    user = User.objects.create(
        email=email,
        phone_country_code=phone_country_code,
        phone_number=phone_number,
        password=make_password(password),
        user_type="ngo"
    )

    ngo_profile = NGOProfile.objects.create(
        user=user,
        ngo_name=ngo_name,
        ngo_services=ngo_service,
        website_url=website_url,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        country=country,
        ngo_registration_number=ngo_registration_number,
        ngo_registration_doc_path=ngo_registration_doc_path,
        ngo_registration_doc_virus_scanned=True if ngo_registration_doc_path else False,
        pan_number=pan_number,
        pan_doc_path=pan_doc_path,
        pan_doc_virus_scanned=True if pan_doc_path else False,
        gst_number=gst_number,
        gst_doc_path=gst_doc_path,
        gst_doc_virus_scanned=True if gst_doc_path else False,
        tan_number=tan_number,
        tan_doc_path=tan_doc_path,
        tan_doc_virus_scanned=True if tan_doc_path else False,
        section8_number=section8_number,
        section8_doc_path=section8_doc_path,
        section8_doc_virus_scanned=True if section8_doc_path else False,
        doc_12a_number=doc_12a_number,
        doc_12a_path=doc_12a_path,
        doc_12a_virus_scanned=True if doc_12a_path else False,
        brand_image_path=brand_image_path,
        brand_image_virus_scanned=True if brand_image_path else False,
        brand_description=brand_description,
        email_otp=email_otp,
        referral_code=referral_code,
    )

    # Save Contact Person
    if contact_person_name and contact_person_phone:
        from .models import ContactPerson
        ContactPerson.objects.create(
            profile_type='ngo',
            profile=user,
            name=contact_person_name,
            phone_country_code=phone_country_code,
            phone_number=contact_person_phone,
            role=contact_person_role,
            otp=contact_person_otp,
            referral_code=referral_code,
            email_otp=email_otp
        )

    return JsonResponse({"success": True, "message": "NGO registered successfully."})

@csrf_protect
@require_POST
def save_advertiser(request):
    data = request.POST
    files = request.FILES
    errors = {}
    

    # Email
    email = data.get("email")
    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."
        if User.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."

    # Password
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    if not password or len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."
        
    email_otp = data.get("otp1")

    # Phone
    phone_country_code = "+91"
    phone_number = data.get("phone")
    if not phone_number or not re.match(r"^\d{10}$", phone_number):
        errors["phone"] = "Enter a valid phone number."

    # Company Info
    company_name = data.get("company_name")
    if not company_name:
        errors["company_name"] = "Company name is required."

    advertiser_type_id = data.get("advertiser_type")
    ad_services_id = data.get("ad_service_req")
    advertiser_type = None
    ad_services = None
    if advertiser_type_id:
        try:
            advertiser_type = AdvertiserType.objects.get(name=advertiser_type_id)
        except Exception as e:
            errors["advertiser_type"] = "Invalid advertiser type selected."
    if ad_services_id:
        try:
            ad_services = AdServiceReq.objects.get(name=ad_services_id)
        except Exception as e:
            errors["ad_service_req"] = "Invalid ad services selected."
    
    website = data.get("website")

    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    pincode = data.get("pincode")
    country = data.get("country")
    if not address:
        errors["address"] = "Address is required."
    if not city:
        errors["city"] = "City is required."
    if not state:
        errors["state"] = "State is required."
    if not country:
        errors["country"] = "Country is required."
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter a valid pincode."

    # Incorporation Doc
    incorporation_number = data.get("incorporation_number")
    if not incorporation_number:
        errors["incorporation_number"] = "Incorporation number is required."
    incorporation_doc_path, err = validate_and_save_file(files.get("incorporation_doc"), "incorporation", "Incorporation Document",user_type="advertiser")
    if not incorporation_doc_path:
        errors["incorporation_doc"] = "Upload incorporation document."
    if err:
        errors["incorporation_doc"] = err

    # GST
    gst_number = data.get("gst_number")
    if not gst_number:
        errors["gst_number"] = "GST number is required."
    gst_doc_path, err = validate_and_save_file(files.get("gst_doc"), "gst", "GST Document",user_type="advertiser")
    if not gst_doc_path:
        errors["gst_doc"] = "Upload GST document."
    if err:
        errors["gst_doc"] = err

    # PAN
    pan_number = data.get("pan_number")
    if not pan_number:
        errors["pan_number"] = "PAN number is required."
    pan_doc_path, err = validate_and_save_file(files.get("pan_doc"), "pan", "PAN Document",user_type="advertiser")
    if not pan_doc_path:
        errors["pan_doc"] = "Upload PAN document."
    if err:
        errors["pan_doc"] = err

    # TAN
    tan_number = data.get("tan_number")
    if not tan_number:
        errors["tan_number"] = "TAN number is required."
    tan_doc_path, err = validate_and_save_file(files.get("tan_doc"), "tan", "TAN Document",user_type="advertiser")
    if not tan_doc_path:
        errors["tan_doc"] = "Upload TAN document."
    if err:
        errors["tan_doc"] = err

    # Brand Image
    brand_image_path, err = validate_and_save_file(files.get("brand_image"), "brand_image", "Brand Image",user_type="advertiser")
    if not brand_image_path:
        errors["brand_image"] = "Upload Image"
    if err:
        errors["brand_image"] = err

    # Description and OTP
    brand_description = data.get("brand_description")
    referral_code = data.get("referral_code")

    # Contact Person
    contact_name = data.get("contact_person_name")
    contact_phone = data.get("contact_person_phone")
    contact_role = data.get("contact_person_role")
    ref_otp = data.get("otp2")
    if not contact_name:
        errors["contact_person_name"] = "Contact person name is required."
    if not contact_phone:
        errors["contact_person_phone"] = "Contact person phone is required."
    if not contact_role:
        errors["contact_person_role"] = "Contact person role is required."

    selfie_path, err = validate_and_save_file(files.get("selfie"), "selfie", "Selfie Upload", user_type="client")
    if err:
        errors["selfie"] = err
    elif not selfie_path:
        errors["selfie"] = "Selfie is required."
    # Return errors if any
    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # Create User
    user = User.objects.create(
        email=email,
        phone_country_code=phone_country_code,
        phone_number=phone_number,
        password=make_password(password),
        user_type="advertiser"
    )

    # Create AdvertiserProfile
    advertiser = AdvertiserProfile.objects.create(
        user=user,
        company_name=company_name,
        advertiser_type=advertiser_type,
        ad_services_required=ad_services,
        website_url=website,
        address=address,
        city=city,
        state=state,
        country=country,
        pincode=pincode,
        incorporation_number=incorporation_number,
        incorporation_doc_path=incorporation_doc_path,
        incorporation_doc_virus_scanned=bool(incorporation_doc_path),
        gst_number=gst_number,
        gst_doc_path=gst_doc_path,
        gst_doc_virus_scanned=bool(gst_doc_path),
        pan_number=pan_number,
        pan_doc_path=pan_doc_path,
        pan_doc_virus_scanned=bool(pan_doc_path),
        tan_number=tan_number,
        tan_doc_path=tan_doc_path,
        tan_doc_virus_scanned=bool(tan_doc_path),
        brand_image_path=brand_image_path,
        brand_image_virus_scanned=bool(brand_image_path),
        brand_description=brand_description,
        email_otp=email_otp,
        referral_code=referral_code,
    )

    # Create ContactPerson if present
    if contact_name and contact_phone:
        ContactPerson.objects.create(
            profile_type='advertiser',
            profile=user,
            name=contact_name,
            phone_country_code=phone_country_code,
            phone_number=contact_phone,
            role=contact_role,
            otp=ref_otp,
            referral_code=referral_code,
            email_otp=email_otp
        )
        

    return JsonResponse({"success": True, "message": "Advertiser registered successfully."})

@csrf_protect
@require_POST
def save_client(request):
    data = request.POST
    files = request.FILES
    errors = {}

    # === BASIC VALIDATION ===
    email = data.get("email").strip()
    password = data.get("password").strip()
    confirm_password = data.get("confirm_password").strip()

    # Email
    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."
        if User.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."
            
    otp_token = data.get("otp_token")
    # if not otp_token:
    #     errors["otp1"] = "Please refresh the page."
    email_otp = data.get("otp1")  # from HTML field "otp1"
    # if not email_otp:
    #     errors["otp1"] = "OTP is required."
    # otp_verification = verify_otp(email, email_otp, otp_token)
    # if not otp_verification["success"]:
    #     errors["otp1"] = otp_verification["message"]

    # Password
    if not password or len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    # Phone
    phone_country_code = "+91"  # default
    phone_number = data.get("phone")
    if not phone_number or not re.match(r"^\d{10}$", phone_number):
        errors["phone"] = "Enter a valid phone number."

    # Company Info
    company_name = data.get("company_name")
    if not company_name:
        errors["company_name"] = "Company name is required."

    company_type_id = data.get("company_type")
    company_service_id = data.get("company_service")
    company_type = None
    company_service = None

    if company_type_id:
        try:
            company_type = ClientType.objects.get(name=company_type_id)
        except Exception as e:
            errors["company_type"] = "Invalid company type."

    if company_service_id:
        try:
            company_service = ClientService.objects.get(name=company_service_id)
        except Exception as e:
            errors["company_service"] = "Invalid company service."

    website = data.get("website")
    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    country = data.get("country")
    pincode = data.get("pincode")

    if not address:
        errors["address"] = "Address is required."
    if not city:
        errors["city"] = "City is required."
    if not state:
        errors["state"] = "State is required."
    if not country:
        errors["country"] = "Country is required."
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter a valid pincode."

    # === DOCUMENTS VALIDATION ===
    incorporation_number = data.get("incorporation")
    if not incorporation_number:
        errors["incorporation"] = "Incorporation number is required."
    incorporation_doc_path, err = validate_and_save_file(files.get("incorporation_doc"), "incorporation", "Incorporation Document", user_type="client")
    if not incorporation_doc_path:
        errors["incorporation_doc"] = "Upload incorporation document."
    if err:
        errors["incorporation_doc"] = err

    gst_number = data.get("gst")
    if not gst_number:
        errors["gst"] = "GST number is required."
    gst_doc_path, err = validate_and_save_file(files.get("gst_doc"), "gst", "GST Document", user_type="client")
    if not gst_doc_path:
        errors["gst_doc"] = "Upload GST document."
    if err:
        errors["gst_doc"] = err

    pan_number = data.get("pan")
    if not pan_number:
        errors["pan"] = "PAN number is required."
    pan_doc_path, err = validate_and_save_file(files.get("pan_doc"), "pan", "PAN Document", user_type="client")
    if not pan_doc_path:
        errors["pan_doc"] = "Upload PAN document."
    if err:
        errors["pan_doc"] = err

    tan_number = data.get("tan")
    if not tan_number:
        errors["tan"] = "TAN number is required."
    tan_doc_path, err = validate_and_save_file(files.get("tan_doc"), "tan", "TAN Document", user_type="client")
    if not tan_doc_path:
        errors["tan_doc"] = "Upload TAN document."
    if err:
        errors["tan_doc"] = err

    # Selfie Upload
    selfie_path, err = validate_and_save_file(files.get("selfie"), "selfie", "Selfie Upload", user_type="client")
    if err:
        errors["selfie"] = err
    elif not selfie_path:
        errors["selfie"] = "Selfie is required."

    # OTP & Referral
    referral_code = data.get("referral_code")
    
    # Contact Person
    contact_name = data.get("contact_name")
    contact_phone = data.get("contact_phone")
    contact_role = data.get("contact_role")
    ref_otp = data.get("ref_otp")
    if not contact_name:
        errors["contact_name"] = "Contact person name is required."
    if not contact_phone:
        errors["contact_phone"] = "Contact person phone number is required."
    if not contact_role:
        errors["contact_role"] = "Contact person role is required."

    # === RETURN IF ERRORS ===
    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # === CREATE USER ===
    user = User.objects.create(
        email=email,
        phone_country_code=phone_country_code,
        phone_number=phone_number,
        password=make_password(password),
        user_type="client"
    )

    # === CREATE CLIENT PROFILE ===
    client = ClientProfile.objects.create(
    user=user,
    company_name=company_name,
    website_url=website,
    address=address,
    city=city,
    state=state,
    country=country,
    pincode=pincode,
    company_type=company_type,
    services_interested=company_service,
    incorporation_number=incorporation_number,
    incorporation_doc_path=incorporation_doc_path,
    incorporation_doc_virus_scanned=bool(incorporation_doc_path),
    gst_number=gst_number,
    gst_doc_path=gst_doc_path,
    gst_doc_virus_scanned=bool(gst_doc_path),
    pan_number=pan_number,
    pan_doc_path=pan_doc_path,
    pan_doc_virus_scanned=bool(pan_doc_path),
    tan_number=tan_number,
    tan_doc_path=tan_doc_path,
    tan_doc_virus_scanned=bool(tan_doc_path),
    email_otp=email_otp,
    referral_code=referral_code,
)

    # === CREATE CONTACT PERSON ===
    if contact_name and contact_phone:
        ContactPerson.objects.create(
            profile_type='client',
            profile=user,
            name=contact_name,
            phone_country_code=phone_country_code,
            phone_number=contact_phone,
            role=contact_role,
            otp=ref_otp,
            referral_code=referral_code,
            email_otp=email_otp
        )
    return JsonResponse({"success": True, "message": "Client registered successfully."})

@csrf_protect
@require_POST
def save_medical_pharmacy(request):
    data = request.POST
    files = request.FILES
    errors = {}

    # Email
    email = data.get("email")
    logger.info(f"Email received: {email}")
    if not email:
        errors["email"] = "Email is required."
        logger.warning("Email is missing")
    else:
        try:
            validate_email(email)
            logger.info("Email validation passed")
        except ValidationError:
            errors["email"] = "Enter a valid email address."
            logger.warning("Email validation failed")
        if User.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."
            logger.warning("Email already exists in database")
            
    # otp_token = data.get("otp_token")
    # if not otp_token:
    #     errors["otp1"] = "Please refresh the page."
    email_otp = data.get("otp1")  # from HTML field "otp1"
    # if not email_otp:
    #     errors["otp1"] = "OTP is required."
    # otp_verification = verify_otp(email, email_otp, otp_token)
    # if not otp_verification["success"]:
    #     errors["otp1"] = otp_verification["message"]

    # Password
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    if not password or len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
        logger.warning(f"Password validation failed - length: {len(password) if password else 0}")
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."
        logger.warning(f"Password mismatch - Password: '{password}' vs Confirm: '{confirm_password}'")
    else:
        logger.info("Password validation passed")

    # Phone
    phone_country_code = "+91"
    phone_number = data.get("phone-number")
    if not phone_number or not re.match(r"^\d{10}$", phone_number):
        errors["phone-number"] = "Enter a valid phone number."

    # Company Info
    company_name = data.get("company-name")
    if not company_name:
        errors["company-name"] = "Company name is required."

    # Get foreign key instances from IDs
    pharmacy_type_id = data.get("pharmacy_type")
    services_offered_id = data.get("services_offered")
    
    # Convert to model instances
    pharmacy_type = None
    services_offered = None
    
    if pharmacy_type_id:
        try:
            pharmacy_type = PharmacyType.objects.get(name=pharmacy_type_id)
        except Exception as e:
            errors["pharmacy_type"] = "Invalid pharmacy type selected."
    
    if services_offered_id:
        try:
            services_offered = PharmacyServices.objects.get(name=services_offered_id)
        except Exception as e:
            errors["services_offered"] = "Invalid service selected."

    website = data.get("website-url")
    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    pincode = data.get("pincode")
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter a valid pincode."

    if not address:
        errors["address"] = "Address is required."
    if not city:
        errors["city"] = "City is required."
    if not state:
        errors["state"] = "State is required."
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter a valid pincode."
        

    # Incorporation Doc
    incorporation_number = data.get("incorporation_number")
    if not incorporation_number:
        errors["incorporation_number"] = "Incorporation number is required."
    incorporation_doc_path, err = validate_and_save_file(files.get("incorporation_doc"), "incorporation", "Incorporation Document",user_type="pharmacy")
    if not incorporation_doc_path:
        errors["incorporation_doc"] = "Upload incorporation document."
    if err:
        errors["incorporation_doc"] = err

    # GST
    gst_number = data.get("gst_number")
    if not gst_number:
        errors["gst_number"] = "GST number is required."
    gst_doc_path, err = validate_and_save_file(files.get("gst_doc"), "gst", "GST Document",user_type="pharmacy")
    if not gst_doc_path:
        errors["gst_doc"] = "Upload GST document."
    if err:
        errors["gst_doc"] = err

    # PAN
    pan_number = data.get("pan_number")
    if not pan_number:
        errors["pan_number"] = "PAN number is required."
    pan_doc_path, err = validate_and_save_file(files.get("pan_doc"), "pan", "PAN Document",user_type="pharmacy")
    if not pan_doc_path:
        errors["pan_doc"] = "Upload PAN document."
    if err:
        errors["pan_doc"] = err

    # TAN
    tan_number = data.get("tan_number")
    if not tan_number:
        errors["tan_number"] = "TAN number is required."
    tan_doc_path, err = validate_and_save_file(files.get("tan_doc"), "tan", "TAN Document",user_type="pharmacy")
    if not tan_doc_path:
        errors["tan_doc"] = "Upload TAN document."
    if err:
        errors["tan_doc"] = err

    # MEDICAL LICENSE
    medical_license_number = data.get("medical_license_number")
    if not medical_license_number:
        errors["medical_license_number"] = "Medical License number is required."
    medical_license_doc_path, err = validate_and_save_file(files.get("medical_license_doc"), "medical_license", "Medical License Document",user_type="pharmacy")
    if not medical_license_doc_path:
        errors["medical_license_doc"] = "Upload Medical License document."
    if err:
        errors["medical_license_doc"] = err

    # Brand Image
    storefront_image_path, err = validate_and_save_file(files.get("store_front"), "store_front", "Storefront Image",user_type="pharmacy")
    if err:
        errors["store_front"] = err

    # Description and OTP
    referral_code = data.get("referral_code")

    # Contact Person
    contact_name = data.get("contact_person_name")
    contact_phone = data.get("contact_person_phone")
    contact_role = data.get("contact_person_role")
    ref_otp = data.get("otp2")
    if not contact_name:
        errors["contact_person_name"] = "Contact person name is required."
    if not contact_phone:
        errors["contact_person_phone"] = "Contact person phone is required."
    if not contact_role:
        errors["contact_person_role"] = "Contact person role is required."

    # Return errors if any
    if errors:
        logger.error(f"Registration failed with errors: {errors}")
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # Create User
    user = User.objects.create(
        email=email,
        phone_country_code=phone_country_code,
        phone_number=phone_number,
        password=make_password(password),
        user_type="pharmacy"
    )

    # Create AdvertiserProfile
    pharmacy = PharmacyProfile.objects.create(
        user=user,
        company_name=company_name,
        pharmacy_type=pharmacy_type,
        services_offered=services_offered,
        website_url=website,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        incorporation_number=incorporation_number,
        incorporation_doc_path=incorporation_doc_path,
        incorporation_doc_virus_scanned=bool(incorporation_doc_path),
        gst_number=gst_number,
        gst_doc_path=gst_doc_path,
        gst_doc_virus_scanned=bool(gst_doc_path),
        pan_number=pan_number,
        pan_doc_path=pan_doc_path,
        pan_doc_virus_scanned=bool(pan_doc_path),
        tan_number=tan_number,
        tan_doc_path=tan_doc_path,
        tan_doc_virus_scanned=bool(tan_doc_path),
        medical_license_number = medical_license_number,
        medical_license_doc_path = medical_license_doc_path,
        medical_license_doc_virus_scanned=bool(medical_license_doc_path),
        storefront_image_path=storefront_image_path,
        storefront_image_virus_scanned=bool(storefront_image_path),
        email_otp=email_otp,
        referral_code=referral_code,
    )

    # Create ContactPerson if present
    if contact_name and contact_phone:
        ContactPerson.objects.create(
            profile_type='pharmacy',
            profile=user,
            name=contact_name,
            phone_country_code=phone_country_code,
            phone_number=contact_phone,
            role=contact_role,
            otp=ref_otp,
            referral_code=referral_code,
            email_otp=email_otp
        )
    logger.info("Medical pharmacy registration completed successfully")
    return JsonResponse({"success": True, "message": "Medical pharmacy registered successfully."})

@csrf_protect
@require_POST
def save_lab(request):
    data = request.POST
    files = request.FILES
    errors = {}

    # Required text fields
    required_fields = {
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "phone": "Phone Number",
        "lab_name": "Lab Name",
        "owner_name": "Owner Name",
        "lab_registration_number": "Lab Registration Number",
        "lab_timing": "Lab Timing",
        "address": "Address",
        "city": "City",
        "state": "State",
        "pincode": "Pincode",
        "country": "Country",
        "lab_certificate_number": "Lab Certificate Number",
        "aadhaar_number": "Aadhaar Number",
        "pan_number": "PAN Number",
        "gov_license_number": "Gov License Number",
        "contact_name": "Contact Person Name",
        "contact_phone": "Contact Person Phone",
    }

    for field, label in required_fields.items():
        if not data.get(field) or data.get(field).strip() == "":
            errors[field] = f"{label} is required."

    # File required fields
    required_files = {
        "lab_certificate": "Lab Certificate",
        "aadhar_doc": "Aadhar Document",
        "pan_doc": "PAN Document",
        "gov_license": "Gov License Document",
        "lab_photo": "Lab Photo",
    }

    for field, label in required_files.items():
        if field not in files:
            errors[field] = f"{label} is required."

    # Multi-select dropdown validations
    services = data.getlist("services")
    facilities = data.getlist("facilities")

    if len(services) == 0:
        errors["services"] = "Select at least one Lab Service."

    if len(facilities) == 0:
        errors["facilities"] = "Select at least one Lab Facility."

    # Email existence check
    email = data.get("email", "").strip()
    if User.objects.filter(email=email).exists():
        errors["email"] = "Email already registered."

    # Password match
    if data.get("password") != data.get("confirm_password"):
        errors["confirm_password"] = "Passwords do not match."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # Save uploaded files
    lab_certificate_path, _ = validate_and_save_file(files["lab_certificate"], "lab_certificate", "", "lab")
    aadhar_path, _ = validate_and_save_file(files["aadhar_doc"], "aadhaar", "", "lab")
    pan_path, _ = validate_and_save_file(files["pan_doc"], "pan", "", "lab")
    license_path, _ = validate_and_save_file(files["gov_license"], "license", "", "lab")
    lab_photo_path, _ = validate_and_save_file(files["lab_photo"], "lab_photo", "", "lab")

    # Create User
    user = User.objects.create(
        email=email,
        phone_country_code="+91",
        phone_number=data.get("phone"),
        password=make_password(data.get("password")),
        user_type="lab"
    )

    # Create Lab Profile
    lab = LabProfile.objects.create(
        user=user,
        lab_name=data.get("lab_name"),
        owner_name=data.get("owner_name"),
        contact_number=data.get("phone"),
        alt_contact_number=data.get("alt_phone"),
        lab_registration_number=data.get("lab_registration_number"),
        lab_certificate_number=data.get("lab_certificate_number"),
        identity_proof_aadhar_number=data.get("aadhaar_number"),
        identity_proof_pan_number=data.get("pan_number"),
        gov_license_number=data.get("gov_license_number"),
        address=data.get("address"),
        city=data.get("city"),
        state=data.get("state"),
        pincode=data.get("pincode"),
        country=data.get("country"),
        lab_timing_id=data.get("lab_timing"),
        lab_certificate_path=lab_certificate_path,
        identity_proof_aadhar_path=aadhar_path,
        identity_proof_pan_path=pan_path,
        gov_license_path=license_path,
        lab_photo_path=lab_photo_path,
        referral_code=data.get("referral_code") if data.get("referral_code") else None,
    )

    # Many-to-Many — Services
    for sid in services:
        LabProfileServices.objects.create(lab=lab, service_id=sid)

    # Many-to-Many — Facilities
    for fid in facilities:
        LabProfileFacilities.objects.create(lab=lab, facility_id=fid)

    # Contact Person
    ContactPerson.objects.create(
        profile_type="lab",
        profile=user,
        name=data.get("contact_name"),
        phone_country_code="+91",
        role=data.get("contact_designation"),
        phone_number=data.get("contact_phone"),
    )

    return JsonResponse({"success": True, "message": "Lab registered successfully!"})

@csrf_protect
@require_POST
def save_hospital(request):
    data = request.POST
    files = request.FILES
    errors = {}

    # Basic Validation
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()
    phone_country_code = "+91"
    phone_number = data.get("phone")

    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Invalid email format."
        if User.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."

    if not password or len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    # Hospital fields
    hospital_name = data.get("hospital_name")
    if not hospital_name:
        errors["hospital_name"] = "Hospital name is required."

    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    pincode = data.get("pincode")

    if not address: errors["address"] = "Address is required."
    if not city: errors["city"] = "City is required."
    if not state: errors["state"] = "State is required."
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter valid pincode."

    # Required Documents
    reg_doc_path, err = validate_and_save_file(files.get("registration_doc"), "registration", "Registration Certificate", "hospital")
    if err: errors["registration_doc"] = err
    if not reg_doc_path: errors["registration_doc"] = "Registration document is required."

    aadhar_doc_path, err = validate_and_save_file(files.get("aadhar_doc"), "aadhar", "Aadhar Document", "hospital")
    if err: errors["aadhar_doc"] = err
    if not aadhar_doc_path: errors["aadhar_doc"] = "Aadhar document is required."

    pan_doc_path, err = validate_and_save_file(files.get("pan_doc"), "pan", "PAN Document", "hospital")
    if err: errors["pan_doc"] = err
    if not pan_doc_path: errors["pan_doc"] = "PAN document is required."

    logo_path, err = validate_and_save_file(files.get("logo"), "hospital_logo", "Hospital Logo", "hospital")
    if err: errors["logo"] = err
    if not logo_path: errors["logo"] = "Hospital logo is required."

    photo_path, err = validate_and_save_file(files.get("photo"), "hospital_photo", "Hospital Photo", "hospital")
    if err: errors["photo"] = err
    if not photo_path: errors["photo"] = "Hospital photo is required."

    # Contact Person
    contact_name = data.get("contact_name")
    contact_phone = data.get("contact_phone")
    contact_role = data.get("contact_role")

    if not contact_name: errors["contact_name"] = "Contact person name required."
    if not contact_phone: errors["contact_phone"] = "Contact person phone required."
    if not contact_role: errors["contact_role"] = "Role required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # Create User
    user = User.objects.create(
        email=email,
        phone_country_code=phone_country_code,
        phone_number=phone_number,
        password=make_password(password),
        user_type="hospital"
    )

    # Profile
    hospital = HospitalProfile.objects.create(
        user=user,
        hospital_name=hospital_name,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        registration_certificate_path=reg_doc_path,
        registration_doc_virus_scanned=True,
        aadhar_doc_path=aadhar_doc_path,
        aadhar_doc_virus_scanned=True,
        pan_doc_path=pan_doc_path,
        pan_doc_virus_scanned=True,
        hospital_logo_path=logo_path,
        hospital_logo_virus_scanned=True,
        hospital_photo_path=photo_path,
        hospital_photo_virus_scanned=True,
    )

    ContactPerson.objects.create(
        profile_type='hospital',
        profile=user,
        name=contact_name,
        phone_number=contact_phone,
        role=contact_role
    )

    return JsonResponse({"success": True, "message": "Hospital registered successfully!"})

@csrf_protect
@require_POST
def save_doctor(request):
    data = request.POST
    files = request.FILES
    errors = {}

    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()
    phone_country_code = "+91"
    phone_number = data.get("phone")

    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Invalid email."
        if User.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."

    if not password or len(password) < 8:
        errors["password"] = "Password must be min 8 chars."
    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    full_name = data.get("full_name")
    if not full_name: errors["full_name"] = "Doctor name is required."

    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    pincode = data.get("pincode")

    if not address: errors["address"] = "Address required."
    if not city: errors["city"] = "City required."
    if not state: errors["state"] = "State required."
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter valid pincode."

    # Related fields (FK)
    specialty_id = data.get("specialty")
    education_id = data.get("education")
    experience_id = data.get("experience")

    try: specialty = DoctorSpeciality.objects.get(id=specialty_id)
    except: errors["specialty"] = "Specialty required."

    try: education = DoctorEducation.objects.get(id=education_id)
    except: errors["education"] = "Education required."

    try: experience = DoctorExperience.objects.get(id=experience_id)
    except: errors["experience"] = "Experience required."

    # Required Docs
    registration_doc_path, err = validate_and_save_file(files.get("registration_doc"), "doctor_reg", "Registration Certificate", "doctor")
    if err or not registration_doc_path: errors["registration_doc"] = "Registration doc required."

    aadhar_path, err = validate_and_save_file(files.get("aadhar_doc"), "aadhar", "Aadhar Document", "doctor")
    if err or not aadhar_path: errors["aadhar_doc"] = "Aadhar required."

    pan_path, err = validate_and_save_file(files.get("pan_doc"), "pan", "PAN Document", "doctor")
    if err or not pan_path: errors["pan_doc"] = "PAN required."

    photo_path, err = validate_and_save_file(files.get("clinic_photo"), "clinic_photo", "Clinic Photo", "doctor")
    if err or not photo_path: errors["clinic_photo"] = "Clinic photo required."

    logo_path, err = validate_and_save_file(files.get("clinic_logo"), "clinic_logo", "Clinic Logo", "doctor")
    if err or not logo_path: errors["clinic_logo"] = "Clinic logo required."

    contact_name = data.get("contact_name")
    contact_role = data.get("contact_role")

    if not contact_name: errors["contact_name"] = "Contact name required."
    if not contact_role: errors["contact_role"] = "Contact role required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # Create User
    user = User.objects.create(
        email=email,
        phone_country_code=phone_country_code,
        phone_number=phone_number,
        password=make_password(password),
        user_type="doctor"
    )

    # Profile
    DoctorProfile.objects.create(
        user=user,
        full_name=full_name,
        specialty=specialty,
        education=education,
        experience=experience,
        full_address=address,
        city=city,
        state=state,
        pincode=pincode,
        registration_certificate_path=registration_doc_path,
        registration_certificate_virus_scanned=True,
        aadhar_doc_path=aadhar_path,
        aadhar_doc_virus_scanned=True,
        pan_doc_path=pan_path,
        pan_doc_virus_scanned=True,
        clinic_photo_path=photo_path,
        clinic_photo_virus_scanned=True,
        clinic_logo_path=logo_path,
        clinic_logo_virus_scanned=True,
    )

    ContactPerson.objects.create(
        profile_type='doctor',
        profile=user,
        name=contact_name,
        role=contact_role,
    )

    return JsonResponse({"success": True, "message": "Doctor registered successfully!"})

@csrf_protect
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"success": False, "errors": {"email": "Email is required"}}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "errors": {"email": "User not found"}}, status=404)

        company_name = "Account"

        if user.user_type == "advertiser" and hasattr(user, "advertiserprofile"):
            company_name = user.advertiserprofile.company_name

        elif user.user_type == "client" and hasattr(user, "clientprofile"):
            company_name = user.clientprofile.company_name

        elif user.user_type == "ngo" and hasattr(user, "ngoprofile"):
            company_name = user.ngoprofile.ngo_name

        elif user.user_type == "pharmacy" and hasattr(user, "pharmacyprofile"):
            company_name = user.pharmacyprofile.company_name

        elif user.user_type == "hospital" and hasattr(user, "hospital_profile"):
            company_name = user.hospital_profile.hospital_name

        elif user.user_type == "lab" and hasattr(user, "lab_profile"):
            company_name = user.lab_profile.lab_name

        elif user.user_type == "doctor" and hasattr(user, "doctor_profile"):
            company_name = user.doctor_profile.clinic_name

        result = async_to_sync(send_forgot_password_email)(user, company_name, "http://localhost:5000")
        return JsonResponse(result)

    return render(request, "login/forgot_password.html")

@csrf_protect
def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, "not_found.html", {"error": "Invalid or expired reset link."}, status=404)

    if not token_obj.is_valid():
        token_obj.delete()
        return render(request, "not_found.html", {"error": "This reset link has expired."}, status=400)

    if request.method == "POST":
        password = request.POST.get("NewPassword")
        confirm_password = request.POST.get("ConfirmPassword")
        errors = {}

        if not password or password != confirm_password:
            errors["confirm_password"] = "Passwords do not match."

        if not password or len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."

        if errors:
            return render(request, "login/reset_password.html", {"token": token, "errors": errors})
        
        user = token_obj.user
        user.password = make_password(password)
        user.save()

        token_obj.delete()
        return redirect("login_page")
    return render(request, "login/reset_password.html", {"token": token})