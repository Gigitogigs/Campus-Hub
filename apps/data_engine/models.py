from django.db import models

# Create your models here.
class AnalyticsLog(models.Model):
    event_type = models.CharField(max_length=50)
    
    #Store HASH, not ID
    user_hash = models.CharField(max_length=255)
    
    #Snapshot of user demographics at time of action
    user_tags = models.JSONField()
    
    #Details of what they clicked
    #e.g., {"category": "Shoes", "price": 500}
    meta_data = models.JSONField()
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'event_type']),
        ]