from django.db import models
from ngopost.models import NGOPost
from registration.models import User

# Create your models here.

class Donation(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('NetBanking', 'Net Banking'),
        ('Wallet', 'Wallet'),
        ('Other', 'Other'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    ngopost = models.ForeignKey(NGOPost, on_delete=models.CASCADE, related_name='donations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_id = models.CharField(max_length=64, unique=True, blank=True, null=True, help_text="Unique order ID for the donation (alphanumeric)")
    payment_date = models.DateTimeField(blank=True, null=True, help_text="Date and time when payment was made")
    gst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="GST amount charged on platform fee")
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Platform fee charged for the donation")
    amount_to_ngo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Amount transferred to NGO after fees")
    transaction_id = models.CharField(max_length=64, unique=True, blank=True, null=True, help_text="Transaction ID (alphanumeric)")
    payment_method = models.CharField(max_length=32, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    pan_number = models.CharField(max_length=32, blank=True, null=True)
    pan_document = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=16, choices=PAYMENT_STATUS_CHOICES, default='Success')
    saved = models.BooleanField(default=False, help_text="Whether the donation is saved/bookmarked by the user")
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Donation by {self.user_id} to post {self.ngopost_id} - {self.amount}"
