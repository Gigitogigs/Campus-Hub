from django.db import models
from apps.core_identity.models import User, University
from django.utils.text import slugify
import uuid
from PIL import Image
from .managers import ActiveManager
# Create your models here.


class SluggedModel(models.Model):
    """
    Abstract base model that automatically generates and ensures unique slugs
    for instances based on their title or name field.
    """
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        abstract = True

    def generate_unique_slug(self, source_value):
        base_slug = slugify(source_value)
        unique_slug = base_slug
        model_class = self.__class__
        while model_class.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            source_value = getattr(self, 'title', None) or getattr(self, 'name', None)
            if source_value:
                self.slug = self.generate_unique_slug(source_value)
        super().save(*args, **kwargs)

class SoftDeleteModel(models.Model):
    """
    Abstract base class providing soft-delete functionality.
    
    Models inheriting from this will automatically use `ActiveManager` as their 
    default manager (`.objects`), ensuring that deleted records (is_deleted=True)
    are hidden from standard querysets. 
    A secondary manager (`.all_objects`) is provided to access all records if needed.
    """
    is_deleted = models.BooleanField(default=False)
    
    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

class Category(SluggedModel):
    """
    Represents a category for grouping HustleListings or Events.
    """
    TYPE_CHOICES = [('EVENT', 'Event'), ('HUSTLE', 'Hustle')]
    
    name = models.CharField(max_length=100)
    cat_type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    icon = models.URLField() # link to Cloudinary icon
    
class Organization(SluggedModel):
    """
    Represents an entity (Business, Club, School) on campus that can post events or hustles.
    Organizations belong strictly to one University.
    """
    TYPE_CHOICES = [('BUSINESS', 'Business'), ('CLUB', 'Club'), ('SCHOOL', 'School')]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    org_type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    is_verified = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='orgs_logos/', blank=True, null=True)
    
    name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Format: +2547xxxxxxxxx. Buyers will click to chat")
    
class HustleListing(SluggedModel, SoftDeleteModel):
    """
    A marketplace listing (product or service) posted by an Organization.
    Implements a soft-delete mechanism via `is_deleted`.
    """
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('SOLD', 'Sold'), ('DRAFT', 'Draft')]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    status = models.CharField(choices=STATUS_CHOICES, default='ACTIVE', max_length=10)
    
    is_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ListingImage(models.Model):
    """
    Image instances securely linked to a HustleListing.
    """
    listing = models.ForeignKey(HustleListing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listings/')
    
class Event(SluggedModel, SoftDeleteModel):
    """
    An event hosted by an Organization within a specific University.
    Implements soft deletion via `is_deleted`.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    image = models.ImageField(upload_to='events/')
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """Returns the event title and the university slug context."""
        return f"{self.title} - {self.university.slug}"

class EventListing(SluggedModel, SoftDeleteModel):
    """
    Additional promotional listing details built around an Event.
    Also implements soft deletion via `is_deleted`.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255)
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    description = models.TextField()
    media = models.FileField(upload_to='event_listing_media/', blank=True, null=True)
    
    posted_at = models.DateTimeField(auto_now_add=True)