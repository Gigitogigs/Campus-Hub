from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from .managers import CustomUserManager

# Create your models here.
class University(models.Model):
    """
    Represents a tenant (University) within the platform.
    
    All market hub data (listings, events, organizations) is scoped strictly
    to the user's University for secure data isolation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    allowed_domains = models.JSONField(default=list)
    #brand_color = models.CharField(max_length=7, default ="#000000")
    
    def __str__(self):
        """Returns the string representation of the University (its name)."""
        return self.name
    
class User(AbstractUser):
    """
    Custom User model representing an authenticated individual.
    
    This model utilizes a UUID as the primary key for security (preventing enumeration),
    and sets the email field as the primary unique identifier for login instead of a username.
    """
    #we replace the default id with UUID for security
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #use email as username
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    #Store hash for analytics
    analytics_hash = models.CharField(max_length=255, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
class StudentProfile(models.Model):
    """
    A profile holding additional campus-related metadata for a verified User.
    
    Users must create a StudentProfile tied to a valid University (via an allowed
    email domain match) to interact with the Market Hub features of that University.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.PROTECT)
    course = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    phone_number = models.CharField(max_length=20, blank=True)
    
class EmailVerification(models.Model):
    """
    Stores 6-digit OTP codes used during the registration flow to verify user emails.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        """
        Checks whether the OTP has expired. Valid for 10 minutes after creation.
        """
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=10)