from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from registration.models import User

class Command(BaseCommand):
    help = 'Delete users who are inactive for more than 2 days'

    def handle(self, *args, **kwargs):
        threshold_time = now() - timedelta(days=2)
        users_to_delete = User.objects.filter(is_active=False, last_login__lt=threshold_time)
        count = users_to_delete.count()
        users_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} user(s) inactive for over 2 days."))
