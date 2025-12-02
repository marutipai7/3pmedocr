from decimal import Decimal
from django.db import models
from django.utils import timezone
from registration.models import User

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
