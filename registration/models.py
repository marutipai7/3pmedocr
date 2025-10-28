import secrets
from django.utils import timezone
from datetime import time
from django.db import models

class AdvertiserType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class AdServiceReq(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class ClientService(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class ClientType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class NGOService(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class PharmacyType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    class Meta:
            db_table = 'pharmacy_type'
            
class PharmacyServices(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    class Meta:
            db_table = 'pharmacy_services'

class PharmacyTiming(models.Model):
    pharmacy = models.ForeignKey("PharmacyProfile", on_delete=models.CASCADE, related_name="timings")
    day_of_week = models.CharField(max_length=20)  # e.g. Monday, Tuesday
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pharmacy.company_name} - {self.day_of_week}: {self.opening_time} to {self.closing_time}"

    class Meta:
        db_table = 'pharmacy_timing'
        unique_together = ('pharmacy', 'day_of_week')

            
class User(models.Model):
    USER_TYPE_CHOICES = [
        ('advertiser', 'Advertiser'),
        ('client', 'Client'),
        ('ngo', 'NGO'),
        ('pharmacy', 'Pharmacy'),
        ('user', 'User'),
    ]
    email = models.EmailField(unique=True)
    phone_country_code = models.CharField(max_length=8, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    user_type = models.CharField(max_length=32, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inapp_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    regulatory_alerts = models.BooleanField(default=True)
    promotions_and_offers = models.BooleanField(default=True)
    quite_mode = models.BooleanField(default=False)
    quite_mode_start_time = models.TimeField(blank=True, null=True, default=time(22, 0))
    quite_mode_end_time = models.TimeField(blank=True, null=True, default=time(6, 0))
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)
    last_login_ip = models.CharField(max_length=45, blank=True, null=True, default=None)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=16, blank=True, null=True)
    pan_number = models.CharField(max_length=32, blank=True, null=True)
    profile_photo_path = models.CharField(max_length=255, blank=True, null=True)
    referral_code = models.CharField(max_length=64, blank=True, null=True)
    otp = models.CharField(max_length=64, blank=True, null=True)
    payment_notifications = models.BooleanField(default=True)
    location_notification = models.BooleanField(default=True)

class UserAddress(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=64, blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
class UserReferral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received')
    created_at = models.DateTimeField(default=timezone.now)
    
class AdvertiserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    advertiser_type = models.ForeignKey(AdvertiserType, on_delete=models.CASCADE, blank=True, null=True)
    ad_services_required = models.ForeignKey(AdServiceReq, on_delete=models.CASCADE, blank=True, null=True)
    website_url = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    incorporation_number = models.CharField(max_length=128, blank=True, null=True)
    incorporation_doc_path = models.CharField(max_length=255, blank=True, null=True)
    incorporation_doc_virus_scanned = models.BooleanField(default=False)
    pan_number = models.CharField(max_length=32, blank=True, null=True)
    pan_doc_path = models.CharField(max_length=255, blank=True, null=True)
    pan_doc_virus_scanned = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=32, blank=True, null=True)
    gst_doc_path = models.CharField(max_length=255, blank=True, null=True)
    gst_doc_virus_scanned = models.BooleanField(default=False)
    tan_number = models.CharField(max_length=32, blank=True, null=True)
    tan_doc_path = models.CharField(max_length=255, blank=True, null=True)
    tan_doc_virus_scanned = models.BooleanField(default=False)
    brand_image_path = models.CharField(max_length=255, blank=True, null=True)
    brand_image_virus_scanned = models.BooleanField(default=False)
    brand_description = models.TextField(blank=True, null=True)
    email_otp = models.CharField(max_length=16, blank=True, null=True)
    referral_code = models.CharField(max_length=64, blank=True, null=True)

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_type = models.ForeignKey(ClientType, on_delete=models.CASCADE, blank=True, null=True)
    services_interested = models.ForeignKey(ClientService, on_delete=models.CASCADE, blank=True, null=True)
    website_url = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    incorporation_number = models.CharField(max_length=128, blank=True, null=True)
    incorporation_doc_path = models.CharField(max_length=255, blank=True, null=True)
    incorporation_doc_virus_scanned = models.BooleanField(default=False)
    pan_number = models.CharField(max_length=32, blank=True, null=True)
    pan_doc_path = models.CharField(max_length=255, blank=True, null=True)
    pan_doc_virus_scanned = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=32, blank=True, null=True)
    gst_doc_path = models.CharField(max_length=255, blank=True, null=True)
    gst_doc_virus_scanned = models.BooleanField(default=False)
    tan_number = models.CharField(max_length=32, blank=True, null=True)
    tan_doc_path = models.CharField(max_length=255, blank=True, null=True)
    tan_doc_virus_scanned = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=16, blank=True, null=True)
    referral_code = models.CharField(max_length=64, blank=True, null=True)
    
class NGOProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ngo_name = models.CharField(max_length=255)
    ngo_services = models.ForeignKey(NGOService, on_delete=models.CASCADE, blank=True, null=True)
    website_url = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    ngo_registration_number = models.CharField(max_length=128, blank=True, null=True)
    ngo_registration_doc_path = models.CharField(max_length=255, blank=True, null=True)
    ngo_registration_doc_virus_scanned = models.BooleanField(default=False)
    pan_number = models.CharField(max_length=32, blank=True, null=True)
    pan_doc_path = models.CharField(max_length=255, blank=True, null=True)
    pan_doc_virus_scanned = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=32, blank=True, null=True)
    gst_doc_path = models.CharField(max_length=255, blank=True, null=True)
    gst_doc_virus_scanned = models.BooleanField(default=False)
    tan_number = models.CharField(max_length=32, blank=True, null=True)
    tan_doc_path = models.CharField(max_length=255, blank=True, null=True)
    tan_doc_virus_scanned = models.BooleanField(default=False)
    section8_number = models.CharField(max_length=128, blank=True, null=True)
    section8_doc_path = models.CharField(max_length=255, blank=True, null=True)
    section8_doc_virus_scanned = models.BooleanField(default=False)
    doc_12a_number = models.CharField(max_length=128, blank=True, null=True)
    doc_12a_path = models.CharField(max_length=255, blank=True, null=True)
    doc_12a_virus_scanned = models.BooleanField(default=False)
    brand_image_path = models.CharField(max_length=255, blank=True, null=True)
    brand_image_virus_scanned = models.BooleanField(default=False)
    brand_description = models.TextField(blank=True, null=True)
    email_otp = models.CharField(max_length=16, blank=True, null=True)
    referral_code = models.CharField(max_length=64, blank=True, null=True)

class PharmacyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # --- Personal Details ---
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    personal_email = models.CharField(max_length=255, blank=True, null=True)
    personal_phone_number = models.CharField(max_length=20, blank=True, null=True)
    personal_pan_number = models.CharField(max_length=50, blank=True, null=True)

    # --- Company Details ---
    company_name = models.CharField(max_length=255)
    pharmacy_type = models.ForeignKey(PharmacyType, on_delete=models.CASCADE, blank=True, null=True)
    services_offered = models.ForeignKey(PharmacyServices, on_delete=models.CASCADE, blank=True, null=True)
    website_url = models.CharField(max_length=255, blank=True, null=True)
    timing_info = models.ManyToManyField('PharmacyTiming', blank=True, related_name='pharmacies')
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)

    # --- Company Documents ---
    incorporation_number = models.CharField(max_length=128, blank=True, null=True)
    incorporation_doc_path = models.CharField(max_length=255, blank=True, null=True)
    incorporation_doc_virus_scanned = models.BooleanField(default=False)
    pan_number = models.CharField(max_length=32, blank=True, null=True)
    pan_doc_path = models.CharField(max_length=255, blank=True, null=True)
    pan_doc_virus_scanned = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=32, blank=True, null=True)
    gst_doc_path = models.CharField(max_length=255, blank=True, null=True)
    gst_doc_virus_scanned = models.BooleanField(default=False)
    tan_number = models.CharField(max_length=32, blank=True, null=True)
    tan_doc_path = models.CharField(max_length=255, blank=True, null=True)
    tan_doc_virus_scanned = models.BooleanField(default=False)
    medical_license_number = models.CharField(max_length=128, blank=True, null=True)
    medical_license_doc_path = models.CharField(max_length=255, blank=True, null=True)
    medical_license_doc_virus_scanned = models.BooleanField(default=False)
    storefront_image_path = models.CharField(max_length=255, blank=True, null=True)
    storefront_image_virus_scanned = models.BooleanField(default=False)

    # --- App Lock Selfie ---
    selfie_path_for_applock = models.CharField(max_length=255, blank=True, null=True)
    selfie_virus_scanned = models.BooleanField(default=False)

    # --- Misc ---
    email_otp = models.CharField(max_length=16, blank=True, null=True)
    referral_code = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.company_name} ({self.user.username})"


class ContactPerson(models.Model):
    PROFILE_TYPE_CHOICES = [
        ('advertiser', 'Advertiser'),
        ('client', 'Client'),
        ('ngo', 'NGO'),
        ('pharmacy', 'Pharmacy'),
    ]
    profile_type = models.CharField(max_length=32, choices=PROFILE_TYPE_CHOICES)
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_country_code = models.CharField(max_length=8, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=128, blank=True, null=True)
    otp = models.CharField(max_length=16, blank=True, null=True)
    referral_code = models.CharField(max_length=64, blank=True, null=True)
    email_otp = models.CharField(max_length=16, blank=True, null=True)

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_token(user):
        token = secrets.token_urlsafe(32)
        return PasswordResetToken.objects.create(user=user, token=token)
    
    def is_valid(self):
        return (timezone.now() - self.created_at).total_seconds() < 1800