import os
import re
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import *
from registration.utils import send_custom_email  
from django.utils import timezone
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

ROLE_TO_TEMPLATE = {
    "login": "login/login.html",
    "customer": "registration/register_user.html",
    "ngoOwner": "registration/ngo_register.html",
    "medicalProvider": "registration/medical_provider_register.html",
    "client": "registration/client_register.html",
    "advertiser": "registration/advertiser_register.html",
}

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

    elif role == "medicalProvider":
        context["medical_provider_types"] = MedicalProviderType.objects.filter(is_active=True)
        context["medical_provider_services"] = MedicalProviderServices.objects.filter(is_active=True)
        context["medical_provider_workingdays"] = MedicalProviderWorkingDays.objects.filter(is_active=True)
    print(context)
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
    otp = data.get("otp1")
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
        otp=otp,
    )
    return JsonResponse({"success": True, "message": "User registered successfully."})

@csrf_protect
@require_POST
def save_ngo(request):
    data = request.POST
    files = request.FILES
    errors = {}
    print(data)

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
            ngo_service = NGOService.objects.get(id=ngo_service_id)
        except NGOService.DoesNotExist:
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
    if brand_image_path and err:
        errors["brand_image"] = err

    brand_description = data.get("brand_description")
    email_otp = data.get("otp1")  # from HTML field "otp1"
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
        print("Validation errors:", errors)
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # --- Save User & NGOProfile ---
    user = User.objects.create(
        email=email,
        phone_country_code=phone_country_code,
        phone_number=phone_number,
        password=make_password(password),
        user_type="ngo"
    )
    print("NGO SErvice", ngo_service)

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
            profile_id=ngo_profile.id,
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
    print(data)

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
            advertiser_type = AdvertiserType.objects.get(id=advertiser_type_id)
        except AdvertiserType.DoesNotExist:
            errors["advertiser_type"] = "Invalid advertiser type selected."
    if ad_services_id:
        try:
            ad_services = AdServiceReq.objects.get(id=ad_services_id)
        except AdServiceReq.DoesNotExist:
            errors["ad_services"] = "Invalid ad services selected."
    print(advertiser_type, ad_services)    
    
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
    print("Incorporation Number:", incorporation_number)
    if not incorporation_number:
        errors["incorporation_number"] = "Incorporation number is required."
    incorporation_doc_path, err = validate_and_save_file(files.get("incorporation_doc"), "incorporation", "Incorporation Document",user_type="advertiser")
    if not incorporation_doc_path:
        errors["incorporation_doc"] = "Upload incorporation document."
    if err:
        errors["incorporation_doc"] = err

    # GST
    gst_number = data.get("gst_number")
    print("GST Number:", gst_number)
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
    print("TAN Number:", tan_number)
    if not tan_number:
        errors["tan_number"] = "TAN number is required."
    tan_doc_path, err = validate_and_save_file(files.get("tan_doc"), "tan", "TAN Document",user_type="advertiser")
    if not tan_doc_path:
        errors["tan_doc"] = "Upload TAN document."
    if err:
        errors["tan_doc"] = err

    # Brand Image
    brand_image_path, err = validate_and_save_file(files.get("brand_image"), "brand", "Brand Image",user_type="advertiser")
    if err:
        errors["brand_image"] = err

    # Description and OTP
    brand_description = data.get("brand_description")
    email_otp = data.get("otp1")
    referral_code = data.get("referral_code")

    # Contact Person
    contact_name = data.get("contact_person_name")
    contact_phone = data.get("contact_person_phone")
    contact_role = data.get("contact_person_role")
    ref_otp = data.get("otp2")
    if not contact_name:
        errors["contact_name"] = "Contact person name is required."
    if not contact_phone:
        errors["contact_phone"] = "Contact person phone is required."
    if not contact_role:
        errors["contact_role"] = "Contact person role is required."

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
            profile_id=user.id,
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
    print(data)

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
            company_type = ClientType.objects.get(id=company_type_id)
        except ClientType.DoesNotExist:
            errors["company_type"] = "Invalid company type."

    if company_service_id:
        try:
            company_service = ClientService.objects.get(id=company_service_id)
        except ClientService.DoesNotExist:
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

    # OTP & Referral
    email_otp = data.get("otp1")
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
            profile_id=user.id,
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
def save_medical_provider(request):
    data = request.POST
    files = request.FILES
    errors = {}
    print(data)

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
    provider_type_id = data.get("provider_type")
    services_offered_id = data.get("services_offered")
    working_days_id = data.get("working_days")
    
    # Convert to model instances
    provider_type = None
    services_offered = None
    working_days = None
    
    if provider_type_id:
        try:
            provider_type = MedicalProviderType.objects.get(id=provider_type_id)
        except MedicalProviderType.DoesNotExist:
            errors["provider_type"] = "Invalid provider type selected."
    
    if services_offered_id:
        try:
            services_offered = MedicalProviderServices.objects.get(id=services_offered_id)
        except MedicalProviderServices.DoesNotExist:
            errors["services_offered"] = "Invalid service selected."
    
    if working_days_id:
        try:
            working_days = MedicalProviderWorkingDays.objects.get(id=working_days_id)
        except MedicalProviderWorkingDays.DoesNotExist:
            errors["working_days"] = "Invalid working days selected."
    
    website = data.get("website-url")
    opening_hours = data.get("opening_time")
    closing_hours = data.get("closing_time")
    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    pincode = data.get("pincode")
    country = data.get("country")
    if not pincode or not re.match(r"^\d{4,10}$", pincode):
        errors["pincode"] = "Enter a valid pincode."
        
    if not opening_hours:
        errors["opening_time"] = "Opening time is required."
    if not closing_hours:
        errors["closing_time"] = "Closing time is required."
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
    incorporation_doc_path, err = validate_and_save_file(files.get("incorporation_doc"), "incorporation", "Incorporation Document",user_type="provider")
    if not incorporation_doc_path:
        errors["incorporation_doc"] = "Upload incorporation document."
    if err:
        errors["incorporation_doc"] = err

    # GST
    gst_number = data.get("gst_number")
    if not gst_number:
        errors["gst_number"] = "GST number is required."
    gst_doc_path, err = validate_and_save_file(files.get("gst_doc"), "gst", "GST Document",user_type="provider")
    if not gst_doc_path:
        errors["gst_doc"] = "Upload GST document."
    if err:
        errors["gst_doc"] = err

    # PAN
    pan_number = data.get("pan_number")
    if not pan_number:
        errors["pan_number"] = "PAN number is required."
    pan_doc_path, err = validate_and_save_file(files.get("pan_doc"), "pan", "PAN Document",user_type="provider")
    if not pan_doc_path:
        errors["pan_doc"] = "Upload PAN document."
    if err:
        errors["pan_doc"] = err

    # TAN
    tan_number = data.get("tan_number")
    if not tan_number:
        errors["tan_number"] = "TAN number is required."
    tan_doc_path, err = validate_and_save_file(files.get("tan_doc"), "tan", "TAN Document",user_type="provider")
    if not tan_doc_path:
        errors["tan_doc"] = "Upload TAN document."
    if err:
        errors["tan_doc"] = err

    # MEDICAL LICENSE
    medical_license_number = data.get("medical_license_number")
    if not medical_license_number:
        errors["medical_license_number"] = "Medical License number is required."
    medical_license_doc_path, err = validate_and_save_file(files.get("medical_license_doc"), "medical_license", "Medical License Document",user_type="provider")
    if not medical_license_doc_path:
        errors["medical_license_doc"] = "Upload Medical License document."
    if err:
        errors["medical_license_doc"] = err

    # Brand Image
    storefront_image_path, err = validate_and_save_file(files.get("store_front"), "store_front", "Storefront Image",user_type="provider")
    if err:
        errors["store_front"] = err

    # Description and OTP
    email_otp = data.get("otp1")
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
        user_type="provider"
    )

    # Create AdvertiserProfile
    provider = MedicalProviderProfile.objects.create(
        user=user,
        company_name=company_name,
        provider_type=provider_type,
        services_offered=services_offered,
        website_url=website,
        working_days = working_days,
        opening_time = opening_hours,
        closing_time = closing_hours,
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
            profile_type='provider',
            profile_id=user.id,
            name=contact_name,
            phone_country_code=phone_country_code,
            phone_number=contact_phone,
            role=contact_role,
            otp=ref_otp,
            referral_code=referral_code,
            email_otp=email_otp
        )
    logger.info("Medical provider registration completed successfully")
    return JsonResponse({"success": True, "message": "Medical provider registered successfully."})