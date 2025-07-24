from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

USER_TYPE = [
    ('advertiser', 'Advertiser'),
    ('client', 'Client'),
    ('ngo', 'NGO'),
    ('provider', 'Medical Provider'),
    ('user', 'User'),
]

class UserColorScheme(models.Model):
    user_type = models.CharField(max_length=32, choices=USER_TYPE, unique=True, verbose_name=_("User Type"))
    color_data = models.JSONField(default=dict, help_text=_("JSON object defining the color variables for this theme (e.g., {'header_bg_color': 'violet-sky'})"))
    is_active = models.BooleanField(default=True, help_text=_("Is the color scheme active for the user type"))

    class Meta:
            verbose_name = _("User Color Scheme")
            verbose_name_plural = _("User Color Schemes")
            ordering = ['user_type']

    def __str__(self):
        return f"Color Scheme for {self.get_user_type_display()}"