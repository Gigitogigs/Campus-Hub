from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from .managers import CustomUserManager

# Create your models here.
class University(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    allowed_domains = models.JSONField(default=list)
    #brand_color = models.CharField(max_length=7, default ="#000000")
    
    def __str__(self):
        return self.name
    
class User(AbstractUser):
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.PROTECT)
    course = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    phone_number = models.CharField(max_length=20, blank=True)
    
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=10)