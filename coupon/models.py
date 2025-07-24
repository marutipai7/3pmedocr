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
            db_table = 'country'  # 👈 Custom table name


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

# --- Coupon Model ---
class Coupon(models.Model):
    advertiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    code = models.CharField(max_length=50, unique=True)
    
    # Dropdown-selected string fields
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
    
    # Redemptions and validity
    max_redemptions = models.PositiveIntegerField()
    validity = models.DateField()
    
    # Image upload
    image = models.FileField(upload_to='coupon_images/')
    
    # Metrics
    redeemed_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    
    # Financial & Payment Details
    displays_per_coupon = models.PositiveIntegerField(default=1)
    rate_per_display = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI Payment'),
        ('gateway', 'Payment Gateway'),
        ('card', 'Credit/Debit Card'),
    ]
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    payment_details = models.JSONField(null=True, blank=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='UPI Payment')
    payment_status = models.CharField(max_length=30, default='Pending')
    final_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Metadata
    saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Computed Properties
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
        return self.gross_invoice_amount - float(self.advance_received)

    @property
    def status(self):
        if self.validity < date.today():
            return "Expired"
        return "Active"
    
    def __str__(self):
        return f"{self.title} ({self.code})"
