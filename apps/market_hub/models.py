from django.db import models
from apps.core_identity.models import User, University
from django.utils.text import slugify
import uuid
from PIL import Image
# Create your models here.

def generate_unique_slug(instance, source_value):
    base_slug = slugify(source_value)
    unique_slug = base_slug
    model_class = instance.__class__
    while model_class.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
    return unique_slug

class Category(models.Model):
    TYPE_CHOICES = [('EVENT', 'Event'), ('HUSTLE', 'Hustle')]
    
    name = models.CharField(max_length=100)
    cat_type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    icon = models.URLField() # link to Cloudinary icon
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)
    
class Organization(models.Model):
    TYPE_CHOICES = [('BUSINESS', 'Business'), ('CLUB', 'Club'), ('SCHOOL', 'School')]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    org_type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    is_verified = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='orgs_logos/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    
    name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Format: +2547xxxxxxxxx. Buyers will click to chat")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)
    
class HustleListing(models.Model):
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('SOLD', 'Sold'), ('DRAFT', 'Draft')]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    
    status = models.CharField(choices=STATUS_CHOICES, default='ACTIVE', max_length=10)
    
    #Soft Delete logic
    is_deleted = models.BooleanField(default=False)
    is_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        super().save(*args, **kwargs)
    
class ListingImage(models.Model):
    listing = models.ForeignKey(HustleListing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listings/')
    
class Event(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(unique=True, blank=True)
    
    image = models.ImageField(upload_to='events/')
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.university.slug}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        super().save(*args, **kwargs)
    
class EventListing(models.Model):
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    description = models.TextField()
    media = models.FileField(upload_to='event_listing_media/', blank=True, null=True)
    
    #Soft Delete logic
    is_deleted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        super().save(*args, **kwargs)