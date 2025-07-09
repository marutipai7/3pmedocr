from django.db import models 
from registration.models import User # This is your custom user model

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
