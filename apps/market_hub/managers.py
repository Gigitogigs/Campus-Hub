from django.db import models

class ActiveManager(models.Manager):
    """
    Custom manager that automatically filters out soft-deleted records.
    
    When used as the default manager (`objects`), standard querysets like 
    `Model.objects.all()` will safely return ONLY active records, preventing 
    deleted content from accidentally surfacing in the platform.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
