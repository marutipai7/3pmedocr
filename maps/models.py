from django.db import models
from registration.models import User
from django.utils import timezone
from mongoengine import (
    FloatField, DateTimeField,
    EmbeddedDocument)


class SavedLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_locations')
    mongo_id = models.CharField(max_length=100)  # MongoDB's ObjectId as string
    amenity_type = models.CharField(max_length=20)  # e.g., hospital, pharmacy
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']
        unique_together = ('user', 'mongo_id')

class SearchHistory(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_clicks')
    mongo_id     = models.CharField(max_length=100)  # ObjectId of the clicked MongoDB document
    amenity_type = models.CharField(max_length=20)   # hospital, pharmacy, etc.
    clicked_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-clicked_at']
        unique_together = ('user', 'mongo_id')

class LocationPoint(EmbeddedDocument):
    timestamp = DateTimeField(required=True)
    lat = FloatField(required=True)
    lng = FloatField(required=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            {'fields': ['lat', 'lng'], 'unique': True}
        ]

class PincodeLocation(models.Model):
    pincode = models.CharField(max_length=6)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = ('pincode', 'latitude', 'longitude')
        ordering = ['pincode']
        
class LocationSearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_search_history')
    query = models.CharField(max_length=255, null=False, blank=False)
    latitude = models.CharField(max_length=64, null=True, blank=True)
    longitude = models.CharField(max_length=64, null=True, blank=True)
    result_label = models.CharField(max_length=512, null=True, blank=True)
    searched_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'location_search_history'
        
# class NavigationHistory(Document):
#     user_id = StringField(required=True)
#     session_id = StringField(required=True, unique=True)

#     start_time = DateTimeField(required=True)
#     end_time = DateTimeField()
#     status = StringField(choices=["completed", "interrupted", "cancelled"], default="completed")

#     from_lat = FloatField()
#     from_lng = FloatField()
#     from_address = StringField()

#     to_lat = FloatField()
#     to_lng = FloatField()
#     to_address = StringField()

#     estimated_distance_km = FloatField()
#     estimated_time_sec = FloatField()

#     actual_distance_km = FloatField()
#     actual_time_sec = FloatField()

#     # Using EmbeddedDocumentListField for telemetry points
#     telemetry = EmbeddedDocumentListField(LocationPoint)

#     stopped_lat = FloatField()
#     stopped_lng = FloatField()
#     stopped_address = StringField()

#     route_geometry = ListField(PointField())        
#     matched_geometry = ListField(PointField())  
    
#     reroute_count = IntField(default=0)
#     average_speed_kph = FloatField()
#     top_speed_kph = FloatField()
    
#     created_at = DateTimeField(default=datetime.now)
#     updated_at = DateTimeField(default=datetime.now)
    
#     class Meta:
#         collection = 'navigation_history'
#         indexes = [
#             {'fields': ['user_id', 'session_id'], 'unique': True},
#             {'fields': ['start_time']},
#             {'fields': ['end_time']},
#             {'fields': ['from_lat', 'from_lng']},
#             {'fields': ['to_lat', 'to_lng']}
#         ]
