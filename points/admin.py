from django.contrib import admin

# Register your models here.
from .models import PointsActionType, PointsHistory

admin.site.register(PointsActionType)
admin.site.register(PointsHistory)