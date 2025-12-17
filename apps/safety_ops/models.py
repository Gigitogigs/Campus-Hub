from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.core_identity.models import User

class Report(models.Model):
    REASON_CHOICES = [
        ('SPAM', 'Spam'),
        ('INAPPROPRIATE', 'Inappropriate Content'),
        ('HARASSMENT', 'Harassment'),
        ('SCAM', 'Potential Scam'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('REVIEWED', 'Reviewed'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]

    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_filed'
    )
    is_anonymous = models.BooleanField(default=False)
    
    # Generic Foreign Key configuration
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255) # CharField to support both UUIDs (Users) and Integers (Listings)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.is_anonymous:
            return f"Report {self.id} (Anonymous)"
        return f"Report {self.id} by {self.reporter.email if self.reporter else 'Deleted User'}"