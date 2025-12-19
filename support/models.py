from django.db import models
from registration.models import User
from django.conf import settings
from django.utils import timezone

class IssueType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user_types = models.JSONField(default=list)
    
    def __str__(self):
        return self.name

class IssueOption(models.Model):
    issue_type = models.ForeignKey(IssueType, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=255)
    user_types = models.JSONField(default=list)

    class Meta:
        unique_together = ('issue_type', 'name')

    def __str__(self):
        return f"{self.issue_type.name} - {self.name}"

class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_tickets')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tickets')
    issue_option = models.ForeignKey(IssueOption, on_delete=models.SET_NULL, null=True, blank=True)
    issue_type = models.ForeignKey(IssueType, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('1', 'Open'),
        ('2', 'In Progress'),
        ('3', 'On Hold'),
        ('4', 'Resolved'),
        ('5', 'Cancelled'),
        ('6', 'Closed'),
    ], default='1')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.CharField(max_length=10, null=True, blank=True)

    def ticket_id(self):
        return f"{10000000 + self.id}"

    def __str__(self):
        creator = self.created_by.username if self.created_by else "Unknown"
        return f"{self.ticket_id()} - {self.issue_option} - by {creator}"

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=100)
    profile_type = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'account_faq'
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question

CHATBOT_USER_TYPE_CHOICES = [
        ('advertiser', 'Advertiser'),
        ('client', 'Client'),
        ('ngo', 'NGO'),
        ('pharmacy', 'Pharmacy'),
        ('user', 'User'),
    ]

class ChatOptionGroup(models.Model):
    user_type = models.CharField(max_length=32, choices=CHATBOT_USER_TYPE_CHOICES, unique=True)
    options_data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chat Option Group"
        verbose_name_plural = "Chat Option Groups"
        ordering = ['user_type'] # Order by user type in admin

    def __str__(self):
        return f"Chat Content for {self.get_user_type_display()} (Active: {self.is_active})"

class UserManagement(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('1', 'Open'),
        ('2', 'In Progress'),
        ('3', 'On Hold'),
        ('4', 'Resolved'),
        ('5', 'Cancelled'),
        ('6', 'Closed'),
    ], default='1')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
class TicketChatMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_ticket_messages')
    sender_type = models.CharField(max_length=10, default='user')
    message_content = models.TextField(null=False, blank=False)
    timestamp = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['timestamp']
    def __str__(self):
        return f"Msg on Ticket {self.ticket.ticket_id()} by {self.sender_type} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
class ChatSupport(models.Model):
    chat_session_id = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sender_type = models.CharField(max_length=20)
    sender_id = models.IntegerField(null=True, blank=True)
    session_status = models.CharField(max_length=20, default="active")
    priority = models.CharField(max_length=20, default="normal")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    message_type = models.CharField(max_length=20, default="text")
    attachment_url = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = "support_chat"


class EmailSupport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    email = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default="pending")
    priority = models.CharField(max_length=20, default="normal")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "support_email"
