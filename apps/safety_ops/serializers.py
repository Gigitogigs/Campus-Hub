from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Report

class ReportCreateSerializer(serializers.ModelSerializer):
    # Client sends "hustlelisting", "event", or "organization"
    model_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = Report
        fields = ['model_name', 'object_id', 'reason', 'description', 'is_anonymous']

    def validate(self, attrs):
        model_name = attrs.get('model_name').lower()
        object_id = attrs.get('object_id')

        # 1. Find the ContentType for the given model name
        ct = None
        allowed_apps = ['market_hub', 'core_identity']
        
        for app_label in allowed_apps:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
                break
            except ContentType.DoesNotExist:
                continue

        if not ct:
            raise serializers.ValidationError({"model_name": "Invalid model name or reporting not allowed for this model."})

        # 2. Verify the object actually exists
        model_class = ct.model_class()
        try:
            if not model_class.objects.filter(pk=object_id).exists():
                # Note: If you use slugs in URLs, you might need to resolve slug to ID here or change object_id to accept slugs
                # For now, assuming the frontend sends the ID (PK) of the item.
                raise serializers.ValidationError({"object_id": "Object not found."})
        except (ValueError, TypeError):
            raise serializers.ValidationError({"object_id": "Invalid ID format for the selected model."})

        attrs['content_type'] = ct
        return attrs

    def create(self, validated_data):
        validated_data.pop('model_name') # Remove helper field
        return Report.objects.create(**validated_data)