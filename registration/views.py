import os
import re
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

ROLE_TO_TEMPLATE = {
    "login": "login/login.html",
    "ngoOwner": "registration/ngo_register.html",
    "client": "registration/client_register.html",
    "advertiser": "registration/advertiser_register.html",

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

    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    remember_me = data.get("remember_me")

    errors = {}

    # ✅ Basic validation
    if not email:
        errors["email"] = "Email is required."
    if not password:
        errors["password"] = "Password is required."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    try:
        user = User.objects.get(email=email)

        # ✅ Password check
        if not check_password(password, user.password):
            return JsonResponse({
                "success": False,
                "errors": {"password": "Invalid email or password."}
            })

        if not user.is_active:
            return JsonResponse({
                "success": False,
                "errors": {"account": "Your account is deleted. Please contact support."}
            })


        BLOCKED_TYPES = ["pharmacy", "doctor", "lab", "hospital"]

        if user.user_type in BLOCKED_TYPES:
            return JsonResponse({
                "success": False,
                "errors": {
                    "account": "Invalid user type for CRM login."
                }
            })

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        request.session['user_id'] = user.id

        if remember_me:
            request.session.set_expiry(60 * 60 * 24 * 30) 
        else:
            request.session.set_expiry(0)  

        dashboard_url = reverse("dashboard")

        return JsonResponse({
            "success": True,
            "redirect": dashboard_url,
            "user_type": user.user_type 
        })

    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "errors": {"password": "Invalid email or password."}
        })

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