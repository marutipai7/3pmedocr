from django.db import models
from django.contrib.postgres.fields import ArrayField
from registration.models import User

USER_TYPE_CHOICES = [
    ('advertiser', 'Advertiser'),
    ('client', 'Client'),
    ('ngo', 'NGO'),
    ('pharmacy', 'Pharmacy'),
    ('user', 'User'),
]

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
        
class SettingMenu(models.Model):
    name = models.CharField(max_length=64)
    url = models.CharField(max_length=255)
    icon = models.CharField(max_length=64)
    order = models.PositiveIntegerField(default=0)
    user_types = ArrayField(
        models.CharField(max_length=32, choices=USER_TYPE_CHOICES),
        help_text="Show this menu to these user types",
    )
    is_active = models.BooleanField(default=True)

class CouponPerformance(models.Model):
    date = models.DateField(auto_now_add=True)
    total_coupons = models.PositiveIntegerField()
    total_redemptions = models.PositiveIntegerField()
    active_coupons = models.PositiveIntegerField()
    days_remaining = models.PositiveIntegerField(help_text="Days left for active coupons validity")

    class Meta:
        ordering = ['-date']
        verbose_name = 'Coupon Performance'
        verbose_name_plural = 'Coupon Performance'

    def __str__(self):
        return f"Performance on {self.date}"
    
class TrendingCoupon(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tag = models.CharField(max_length=50, default="COUPON")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CalendarEvent(models.Model):
    COLOR_CHOICES = [
        ('bg-slate-blue', 'Blue'),
        ('bg-strong-red', 'Red'),
        ('bg-green', 'Green'),
        ('bg-vivid-orange', 'Orange'),
        ('bg-purple', 'Purple'),
        ('bg-pink', 'Pink'),
        ('bg-teal', 'Teal'),
        ('bg-dark-blue', 'Dark Blue'),
        ('bg-dark-green', 'Dark Green'),
        ('bg-dark-purple', 'Dark Purple'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='bg-slate-blue')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} on {self.date} at {self.time}"
    
    def get_color_hex(self):
        """Return the hex color value for the event's color class"""
        color_map = {
            'bg-slate-blue': '#64748b',
            'bg-strong-red': '#dc2626',
            'bg-green': '#16a34a',
            'bg-vivid-orange': '#ea580c',
            'bg-purple': '#9333ea',
            'bg-pink': '#ec4899',
            'bg-teal': '#0d9488',
            'bg-dark-blue': '#1e40af',
            'bg-dark-green': '#15803d',
            'bg-dark-purple': '#7c3aed',
        }
        return color_map.get(self.color, '#64748b')  # Default to slate-blue if not found
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    message = models.TextField(null=False, blank=False)
    
    reference_type = models.CharField(max_length=100, null=True, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)

    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"