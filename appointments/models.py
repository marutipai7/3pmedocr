from decimal import Decimal
from django.db import models
from django.utils import timezone
from registration.models import User, UserAddress, LabProfile

class PaymentMethodEnum(models.TextChoices):
    UPI = "UPI", "UPI"
    CARD = "Card", "Card"
    NETBANKING = "NetBanking", "NetBanking"
    WALLET = "Wallet", "Wallet"
    OTHER = "Other", "Other"

class PaymentStatusEnum(models.TextChoices):
    SUCCESS = "Success", "Success"
    FAILED = "Failed", "Failed"

class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id", related_name="payment_methods")

    card_holder_name = models.CharField(max_length=255, null=False, blank=False)
    card_number_masked = models.CharField(max_length=255, null=False, blank=False)
    card_type = models.CharField(max_length=50, null=False, blank=False)
    expiry_month = models.IntegerField(null=False, blank=False)
    expiry_year = models.IntegerField(null=False, blank=False)
    is_default = models.BooleanField(default=False)
    payment_gateway = models.CharField(max_length=50, default="razorpay")
    status = models.CharField(max_length=50, default="active")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_methods"

    def __str__(self):
        return f"{self.card_type} ending with {self.card_number_masked[-4:]}"

class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    order_id = models.CharField(max_length=64, null=True, blank=True)
    tranx_id = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=50)

    points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "wallet_transactions"


class LabTestType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "labtest_type"

    def __str__(self):
        return self.name


class LabTestDescription(models.Model):
    description = models.TextField()

    class Meta:
        db_table = "labtest_description"

    def __str__(self):
        return self.description[:50]


class LabTestPackages(models.Model):
    packages = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "labtest_packages"

    def __str__(self):
        return self.packages


class AppointmentStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    ACCEPTED = "Accepted", "Accepted"
    COMPLETED = "Completed", "Completed"
    CANCELLED = "Cancelled", "Cancelled"


class LabAppointments(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lab_appointments"
    )
    address = models.ForeignKey(
        "registration.UserAddress",
        on_delete=models.CASCADE,
        related_name="lab_appointments",
    )

    test_type = models.ForeignKey(
        LabTestType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="lab_appointments",
    )
    test_description = models.ForeignKey(
        LabTestDescription,
        on_delete=models.SET_NULL,
        null=True,
        related_name="lab_appointments",
    )
    test_package = models.ForeignKey(
        LabTestPackages,
        on_delete=models.SET_NULL,
        null=True,
        related_name="lab_appointments",
    )

    preferred_mode = models.CharField(max_length=20, null=True, blank=True)
    service_type = models.CharField(max_length=20, null=True, blank=True)
    preferred_date_time = models.DateTimeField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING
    )

    accepted_bid = models.ForeignKey(
        "LabBidding",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_lab_appointments"
    )
    accepted_lab = models.ForeignKey(
        "registration.LabProfile",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="accepted_lab_appointments"
    )

    accepted_total_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lab_appointments"

    def __str__(self):
        return f"Appointment #{self.id} - {self.user}"
    
class LabBidStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class LabBidding(models.Model):
    appointment = models.ForeignKey(
        "LabAppointments",
        on_delete=models.CASCADE,
        related_name="lab_bids"
    )
    lab = models.ForeignKey(
        "registration.LabProfile",
        on_delete=models.CASCADE,
        related_name="bids"
    )

    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.IntegerField()  # hours
    remarks = models.CharField(max_length=255, null=True, blank=True)

    bid_status = models.CharField(
        max_length=20,
        choices=LabBidStatus.choices,
        default=LabBidStatus.PENDING
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lab_bidding"

    def __str__(self):
        return f"Bid #{self.id} - {self.lab}"


class LabTestCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "lab_test_category"

    def __str__(self):
        return self.name


class LabTestPackageMaster(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        LabTestCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="test_packages"
    )

    class Meta:
        db_table = "lab_test_package_master"

    def __str__(self):
        return self.name


class LabModeType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "lab_mode_type"

    def __str__(self):
        return self.name


class LabRegion(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "lab_region"

    def __str__(self):
        return self.name


class LabRatePackage(models.Model):
    lab = models.ForeignKey(
        "registration.LabProfile",
        on_delete=models.CASCADE,
        related_name="rate_packages"
    )
    category = models.ForeignKey(
        LabTestCategory,
        on_delete=models.CASCADE,
        related_name="rate_packages"
    )
    test_package = models.ForeignKey(
        LabTestPackageMaster,
        on_delete=models.CASCADE,
        related_name="rate_packages"
    )

    days = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lab_rate_package"

    def __str__(self):
        return f"{self.test_package.name} - {self.lab}"


class LabRateMode(models.Model):
    lab = models.ForeignKey(
        "registration.LabProfile",
        on_delete=models.CASCADE,
        related_name="rate_modes"
    )
    mode_type = models.ForeignKey(
        LabModeType,
        on_delete=models.CASCADE,
        related_name="rate_modes"
    )
    region = models.ForeignKey(
        LabRegion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rate_modes"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lab_rate_mode"

    def __str__(self):
        return f"{self.mode_type.name} - {self.lab}"


class LabSubscription(models.Model):
    lab = models.ForeignKey(
        "registration.LabProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    plan_name = models.CharField(max_length=100, default="Free")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lab_subscription"

    def __str__(self):
        return f"{self.lab} - {self.plan_name}"


class LabAutoBidSettings(models.Model):
    lab = models.ForeignKey(
        "registration.LabProfile",
        on_delete=models.CASCADE,
        related_name="auto_bid_settings"
    )

    is_enabled = models.BooleanField(default=False)
    bid_type = models.CharField(max_length=50, default="percentage")  # percentage / fixed
    bid_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_time = models.IntegerField(default=24)  # hours

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lab_auto_bid_settings"

    def __str__(self):
        return f"{self.lab} - AutoBid: {self.is_enabled}"