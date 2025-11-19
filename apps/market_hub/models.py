from django.db import models
from apps.core_identity.models import User, University

# Create your models here.
class Category(models.Model):
    TYPE_CHOICES = [('EVENT', 'Event'), ('HUSTLE', 'Hustle')]
    
    name = models.CharField(max_length=100)
    cat_type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    icon = models.URLField() # link to Cloudinary icon
    
class Organization(models.Model):
    TYPE_CHOICES = [('BUSINESS', 'Business'), ('CLUB', 'Club'), ('SCHOOL', 'School')]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    org_type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    is_verified = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='orgs_logos/')
    
class HustleListing(models.Model):
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('SOLD', 'Sold'), ('DRAFT', 'Draft')]
    
    Organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    Category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    status = models.CharField(choices=STATUS_CHOICES, default='ACTIVE', max_length=10)
    
    #Soft Delete logic
    is_deleted = models.BooleanField(default=False)
    is_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ListingImage(models.Model):
    listing = models.ForeignKey(HustleListing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listings/')