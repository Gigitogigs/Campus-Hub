from django.contrib import admin
from .models import University, User, StudentProfile

# Register your models here.
admin.site.register(University)
admin.site.register(User)
admin.site.register(StudentProfile)