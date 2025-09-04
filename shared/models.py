from django.db import models
from registration.models import User
from datetime import date
# Create your models here.


# class Shared(models.Model):
#     STATUS_CHOICES = [
#         ("Completed", "Completed"),
#         ("Processing", "Processing"),
#         ("Failed", "Failed"),
#     ]
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date_time = models.DateTimeField()
#     format = models.CharField(max_length=50)
#     type = models.CharField(max_length=100)
#     file_path = models.CharField(max_length=255, blank=True, null=True)
#     doctor = models.CharField(max_length=100)
#     patient = models.CharField(max_length=100)
#     points = models.IntegerField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "shared"   # 👈 replace with your table name

#     def __str__(self):
#         return f"{self.type} - {self.status}"