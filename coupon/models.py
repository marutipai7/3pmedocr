from django.db import models
from registration.models import User
from datetime import date
# --- Dropdown Options ---
class CategoryOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class BrandOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class OfferTypeOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class CountryOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name
    class Meta:
            db_table = 'country'

class StateOption(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(CountryOption, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name
    class Meta:
            db_table = 'state' 

class CityOption(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(StateOption, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name
    class Meta:
            db_table = 'city' 

class PincodeOption(models.Model):
    code = models.CharField(max_length=20, unique=True)
    city = models.ForeignKey(CityOption, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.code
    class Meta:
            db_table = 'pincode' 

class AgeOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    specific_to = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name
    class Meta:
            db_table = 'age' 

class GenderOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name
    class Meta:
            db_table = 'gender' 

class SpendingPowerOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    specific_to = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name
    class Meta:
            db_table = 'spending_power' 

class PaymentMethodEnum(models.TextChoices):
    UPI = "UPI"
    CARD = "Card"
    NETBANKING = "NetBanking"
    WALLET = "Wallet"
    OTHER = "Other"

class PaymentStatusEnum(models.TextChoices):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    
class Coupon(models.Model):
    advertiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    code = models.CharField(max_length=50, unique=True)
    
    category = models.ForeignKey(CategoryOption, on_delete=models.SET_NULL, null=True)
    brand_name = models.ForeignKey(BrandOption, on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(CountryOption, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(StateOption, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(CityOption, on_delete=models.SET_NULL, null=True)
    pincode = models.ForeignKey(PincodeOption, on_delete=models.SET_NULL, null=True)
    age_group = models.ForeignKey(AgeOption, on_delete=models.SET_NULL, null=True)
    gender = models.ForeignKey(GenderOption, on_delete=models.SET_NULL, null=True)
    spending_power = models.ForeignKey(SpendingPowerOption, on_delete=models.SET_NULL, null=True)
    offer_type = models.ForeignKey(OfferTypeOption, on_delete=models.SET_NULL, null=True)
    max_redemptions = models.PositiveIntegerField()
    validity = models.DateField(null=False, blank=False)
    image = models.CharField(max_length=255, null=True, blank=True)
    redeemed_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    displays_per_coupon = models.PositiveIntegerField(default=1)
    rate_per_display = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_details = models.JSONField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodEnum.choices, default=PaymentMethodEnum.UPI)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusEnum.choices, default=PaymentStatusEnum.PENDING)
    final_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def coupon_balance(self):                                              ## coupon.coupon_balance
        return self.max_redemptions - self.redeemed_count

    @property
    def total_value_before_gst(self):
        return self.max_redemptions * self.displays_per_coupon * float(self.rate_per_display)

    @property
    def gst_value(self):
        return self.total_value_before_gst * 0.18

    @property
    def gross_invoice_amount(self):
        return self.total_value_before_gst + self.gst_value

    @property
    def net_payable(self):
        return self.gross_invoice_amount

    @property
    def status(self):
        if self.validity < date.today():
            return "Expired"
        return "Active"
    
    def __str__(self):
        return f"{self.title} ({self.code})"

class CouponClaimed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claimed_coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='claims')
    date_claimed = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.user.username} claimed {self.coupon.code}"
    
    class Meta:
        db_table = "points_couponclaimed"

class DiscountType(models.TextChoices):
    PERCENTAGE = "percentage", "percentage"
    FIXED = "fixed", "fixed"

class SellerCoupon(models.Model):
    seller_type = models.CharField(max_length=50, null=False, blank=False)
    seller_id = models.IntegerField(null=False, blank=False)
    coupon_name = models.CharField(max_length=255, null=False, blank=False)
    coupon_code = models.CharField(max_length=100, unique=True, null=False, blank=False)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    expiry_date = models.DateTimeField(null=False, blank=False)
    usage_limit = models.IntegerField(default=0)
    used_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seller_coupon"