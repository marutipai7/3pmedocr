from django.db import models
from django.contrib.postgres.fields import ArrayField

USER_TYPE_CHOICES = [
    ('advertiser', 'Advertiser'),
    ('client', 'Client'),
    ('ngo', 'NGO'),
    ('provider', 'Medical Provider'),
    ('user', 'User'),
]

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
