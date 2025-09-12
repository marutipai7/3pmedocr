# subscription/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from registration.models import User

class SubscriptionPlan(models.Model):
    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
        ('free', 'Free'),
    ]

    name = models.CharField(max_length=100)   # e.g., "Basic", "Standard"
    subtitle = models.CharField(max_length=150, blank=True, null=True)  # e.g., (Free), (Custom)
    description = models.TextField(blank=True, null=True)  # Optional extra info
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # e.g., 25000
    currency = models.CharField(max_length=10, default="₹")
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CHOICES, default='monthly')
    discount_text = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Incl. Quarterly 10% Disc"
    is_custom_pricing = models.BooleanField(default=False)  # For Enterprise plan

    button_text = models.CharField(max_length=50, default="Subscribe")  
    is_active = models.BooleanField(default=True)  

    display_order = models.PositiveIntegerField(default=0)

     # New field for icon
    icon_path = models.CharField(max_length=255, blank=True, null=True, 
                                 help_text="Path to the plan icon in static files, e.g., 'images/Subscription_Basic.svg'")


    class Meta:
        db_table = "Subscription_Plans"
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} ({self.billing_cycle})"


class Feature(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, related_name="features", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)  
    is_included = models.BooleanField(default=True)  
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "Subscription_Features"
        verbose_name = "Subscription Feature"
        verbose_name_plural = "Subscription Features"

    def __str__(self):
        return f"{'✔' if self.is_included else '✖'} {self.text}"

class SubscriptionHistory(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey("SubscriptionPlan", on_delete=models.CASCADE, related_name="subscriptions")

    activation_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    license_count = models.PositiveIntegerField(default=1)  

    # 💰 New fields for payment details
    billing_cycle = models.CharField(max_length=50, blank=True, null=True)   # e.g. "Monthly", "Quarterly", "Yearly"
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_payable = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activation_date"]

    def __str__(self):
        return f"{self.user} - {self.plan.name} ({self.status})"

    def save(self, *args, **kwargs):
        # Auto update status if expired
        if self.expiry_date < timezone.now():
            self.status = 'expired'
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Returns True if subscription is currently active"""
        return self.status == 'active' and self.expiry_date >= timezone.now()

    def extend_subscription(self, months=1):
        """Extend subscription duration"""
        if self.expiry_date < timezone.now():
            # If already expired, restart from now
            self.activation_date = timezone.now()
            self.expiry_date = self.activation_date + timedelta(days=30*months)
            self.status = 'active'
        else:
            # If active, extend from current expiry
            self.expiry_date += timedelta(days=30*months)
        self.save()