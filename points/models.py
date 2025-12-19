from django.db import models 
from registration.models import User
from django.utils import timezone

class PointsActionType(models.Model):
    action_type = models.CharField(max_length=32, unique=True)
    default_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.default_points} pts"

class PointsHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="points_history")
    action_type = models.ForeignKey(PointsActionType, on_delete=models.CASCADE, related_name="history")
    points = models.PositiveIntegerField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} - {self.action_type.action_type} - {self.points} pts"

class PointsBadge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    min_points = models.PositiveIntegerField()
    max_points = models.PositiveIntegerField(null=True, blank=True) 
    description = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['min_points']

    def _str_(self):
        if self.max_points:
            return f"{self.name} ({self.min_points} - {self.max_points} pts)"
        return f"{self.name} ({self.min_points}+ pts)"
    