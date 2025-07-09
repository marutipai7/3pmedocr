from django.db import models
from django.utils import timezone
from registration.models import User
class NGOPost(models.Model):
    """
    Model to store NGO posts for fundraising.
    """
    class Status(models.TextChoices):
        ONGOING = 'Ongoing', 'Ongoing'
        CLOSED = 'Closed', 'Closed'
        PAUSED = 'Paused', 'Paused'

    class PostType(models.TextChoices):
        EDUCATION = 'Education', 'Education'
        HEALTH = 'Health', 'Health'
        FOOD = 'Food', 'Food'

    class DonationFrequency(models.TextChoices):
        ONETIME = 'One-time', 'One-time'
        WEEKLY = 'Weekly', 'Weekly'
        MONTHLY = 'Monthly', 'Monthly'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ngo_posts')

    header = models.CharField(max_length=80)
    description = models.TextField(max_length=500)
    tags = models.CharField(max_length=255, help_text="Comma-separated tags")
    post_type = models.CharField(max_length=20, choices=PostType.choices)
    
    donation_frequency = models.CharField(
        max_length=20, 
        choices=DonationFrequency.choices, 
        default=DonationFrequency.ONETIME
    )
    target_donation = models.DecimalField(max_digits=12, decimal_places=2)
    donation_received = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00
    )

    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    age_group = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    spending_power = models.CharField(max_length=100, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()
    
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.ONGOING
    )
    
    creative1 = models.FileField(upload_to='ngo_docs/post_creatives/')
    creative2 = models.FileField(upload_to='ngo_docs/post_creatives/', blank=True, null=True)

    views = models.PositiveIntegerField(default=0)
    saved = models.BooleanField(default=False)
    last_downloaded = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.header

    def update_status_if_needed(self):
        """
        Updates the post status to 'Closed' if the end date has passed
        and the status is currently 'Ongoing'.
        """
        if self.status == self.Status.ONGOING and self.end_date < timezone.now().date():
            self.status = self.Status.CLOSED
            self.save(update_fields=['status', 'updated_at'])

    @classmethod
    def bulk_auto_close(cls):
        """
        Bulk update all posts with status 'Ongoing' and end_date in the past to 'Closed'.
        """
        from django.utils import timezone
        now = timezone.now().date()
        cls.objects.filter(status=cls.Status.ONGOING, end_date__lt=now).update(status=cls.Status.CLOSED)

class PostTypeOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class DonationFrequencyOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class CountryOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class StateOption(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(CountryOption, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.country.name})"

class CityOption(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(StateOption, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.state.name})"

class AgeOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class GenderOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class SpendingPowerOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

