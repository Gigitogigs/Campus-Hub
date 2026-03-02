from django.shortcuts import render
from apps.core_identity.models import User

# Create your views here.
from rest_framework import generics, permissions, status, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from .models import HustleListing, Organization, Event, Category, EventListing
from .serializers import (
    HustleListingSerializer,
    OrganizationSerializer,
    EventSerializer,
    CategorySerializer,
    EventListingSerializer,
)
from .permissions import HasStudentProfile, IsOwnerOrReadOnly

# Organization Views
class OrganizationListCreateView(generics.ListCreateAPIView):
    """
    Lists and creates Organizations within the user's University context.
    
    Creation automatically ties the new Organization to the requesting User (as owner)
    and to their associated University.
    """
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]

    def get_queryset(self):
        # Users can only see organizations in their university
        return Organization.objects.filter(university=self.request.user.studentprofile.university)

    def perform_create(self, serializer):
        # Automatically assign owner and university on creation
        serializer.save(
            owner=self.request.user,
            university=self.request.user.studentprofile.university
        )

class OrganizationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Manages specific Organizations.
    
    Users can only retrieve Organizations belonging to their University.
    Update and Destroy actions are strictly limited to the Organization's owner via custom permissions.
    """
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile, IsOwnerOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        # Users can only interact with organizations in their university
        return Organization.objects.filter(university=self.request.user.studentprofile.university)

# Category Views
class CategoryListView(generics.ListAPIView):
    """
    Lists all available Categories (publicly accessible).
    Used primarily to populate frontend dropdowns for Events and Hustles.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()

# Hustle Listing Views
@extend_schema_view(
    get=extend_schema(
        summary="List Hustles",
        description="Retrieve a list of all hustle listings available within your university. You can filter by category, price, or search by title."
    ),
    post=extend_schema(
        summary="Create a Hustle",
        description="Create a new hustle listing. You must have a student profile to perform this action."
    )
)
class HustleListingListCreateView(generics.ListCreateAPIView):
    """
    Lists and creates HustleListings (Marketplace items).
    
    Results are filtered automatically to the user's University and exclude soft-deleted items.
    Users can further filter the list by Category, Price, or search by text.
    """
    serializer_class = HustleListingSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price', 'status', 'organization']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        return HustleListing.objects.filter(university=user.studentprofile.university, is_deleted=False)

    def perform_create(self, serializer):
        # Automatically assign the university based on the user's profile
        serializer.save(university=self.request.user.studentprofile.university)

class HustleListingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Manages specific HustleListings.
    
    Deletion is handled via 'soft-delete' flag marking `is_deleted = True` instead of a hard database destruction.
    Only the listing's Organization owner can mutate the object.
    """
    serializer_class = HustleListingSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile, IsOwnerOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        return HustleListing.objects.filter(university=user.studentprofile.university, is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Event Views
class EventListCreateView(generics.ListCreateAPIView):
    """
    Lists and creates University Events.
    
    Results are automatically scoped to the user's University and exclude soft-deleted events.
    Users can perform text searches or filter by date and category.
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'date_time']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['date_time', 'created_at']

    def get_queryset(self):
        return Event.objects.filter(university=self.request.user.studentprofile.university, is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(university=self.request.user.studentprofile.university)

class EventRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Manages specific Events.
    
    Deletions are handled using a 'soft-delete' mechanism.
    Only the owner of the Organization that created the Event can mutate it.
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile, IsOwnerOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Event.objects.filter(university=self.request.user.studentprofile.university, is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Event Listing Views
class EventListingListCreateView(generics.ListCreateAPIView):
    """
    Lists and creates promotional EventListings connected to an Event.
    
    Checks are performed during creation to ensure that the user posting the listing
    actually owns the Organization running the referenced Event.
    """
    serializer_class = EventListingSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['posted_at', 'created_at']

    def get_queryset(self):
        return EventListing.objects.filter(university=self.request.user.studentprofile.university, is_deleted=False)

    def perform_create(self, serializer):
        event = serializer.validated_data.get('event')
        if event.organization.owner != self.request.user:
            raise serializers.ValidationError({"detail": "You can only create listings for events managed by your own organization."})
        serializer.save(university=self.request.user.studentprofile.university)
        
class EventListingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Manages specific EventListings.
    Operations are limited to the user's University context, with soft-deletion handling 
    and strict owner mutation permissions.
    """
    serializer_class = EventListingSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile, IsOwnerOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return EventListing.objects.filter(university=self.request.user.studentprofile.university, is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)