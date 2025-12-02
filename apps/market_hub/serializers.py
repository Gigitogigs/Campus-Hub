from rest_framework import serializers
from .models import HustleListing, Organization, Category, ListingImage, Event, EventListing
from apps.core_identity.models import User

class MultipleFileField(serializers.ListField):
    child = serializers.FileField()

class OrganizationSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('owner', 'university', 'is_verified')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = '__all__'


class HustleListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    uploaded_images = MultipleFileField(write_only=True, required=False)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name',
        read_only=False
    )
    organization = serializers.SlugRelatedField(
        queryset=Organization.objects.all(),
        slug_field='name',
        read_only=False
    )

    class Meta:
        model = HustleListing
        fields = '__all__'
        read_only_fields = ('university', 'is_deleted', 'is_updated', 'created_at')

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        hustle_listing = HustleListing.objects.create(**validated_data)
        for image in uploaded_images:
            ListingImage.objects.create(listing=hustle_listing, image=image)
        return hustle_listing


class EventSerializer(serializers.ModelSerializer):
    organization = serializers.SlugRelatedField(slug_field='name', read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('university', 'is_deleted', 'created_at')


class EventListingSerializer(serializers.ModelSerializer):
    organization = serializers.SlugRelatedField(slug_field='name', read_only=True)
    event = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = EventListing
        fields = '__all__'
        read_only_fields = ('organization', 'university', 'is_deleted', 'posted_at')