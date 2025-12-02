from django.contrib import admin
from .models import HustleListing, Organization

# Register your models here.
admin.site.register(HustleListing)
admin.site.register(Organization)