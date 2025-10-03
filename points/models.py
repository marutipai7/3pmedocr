from django.db import models 
from registration.models import User
from coupon.models import Coupon 

# Table 1: Action types and their fixed point values
class PointsActionType(models.Model):
    ACTION_CHOICES = [
        ('referral', 'Referral'),
        ('map', 'Map'),
        ('post', 'Post'),
        ('share', 'Share'),
        ('coupon', 'Coupon'),
        ('donation', 'Donation'),
        ('orders', 'Orders'),
        ('subscription', 'Subscription'),
        ('purchase', 'Purchase'),
    ]

    action_type = models.CharField(max_length=32, choices=ACTION_CHOICES, unique=True)
    default_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.default_points} pts"

# Table 2: Points earned per user action
class PointsHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.ForeignKey(PointsActionType, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)  # "Date & Time" column

    def __str__(self):
        return f"{self.user.email} - {self.action_type.action_type} - {self.points} pts"

class PointsBadge(models.Model):
    name = models.CharField(max_length=100)
    min_points = models.PositiveIntegerField()
    max_points = models.PositiveIntegerField(null=True, blank=True)  # NULL for "no upper limit"
    description = models.TextField()
    image_url = models.CharField(max_length=255, blank=True, null=True)  # Or use ImageField if you're uploading

    class Meta:
        ordering = ['min_points']

    def _str_(self):
        if self.max_points:
            return f"{self.name} ({self.min_points} - {self.max_points} pts)"
        return f"{self.name} ({self.min_points}+ pts)"
    
class CouponClaimed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claimed_coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='claims')
    date_claimed = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.user.username} claimed {self.coupon.code}"