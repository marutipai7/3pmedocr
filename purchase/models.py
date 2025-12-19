from django.db import models
from django.utils import timezone
from registration.models import User

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items", db_column="user_id")
    medicine_mongo_id = models.CharField(max_length=50, db_index=True)
    quantity = models.IntegerField(default=1)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "wishlist_medicines"
        indexes = [
            models.Index(fields=["medicine_mongo_id"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.medicine_mongo_id} x{self.quantity}"
