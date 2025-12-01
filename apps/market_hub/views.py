from django.shortcuts import render
from apps.core_identity.models import User

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import HustleListing, Organization, Event, Category, EventListing
from .serializers import (
    HustleListingSerializer,
    OrganizationSerializer,
    EventSerializer,
    CategorySerializer,
    EventListingSerializer,
)
from .permissions import HasStudentProfile

# Organization Views
class OrganizationListCreateView(generics.ListCreateAPIView):
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
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]
    lookup_field = 'slug'
    
    def get_queryset(self):
        # Users can only interact with organizations in their university
        return Organization.objects.filter(university=self.request.user.studentprofile.university)

# Category Views
class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()

# Hustle Listing Views
class HustleListingListCreateView(generics.ListCreateAPIView):
    serializer_class = HustleListingSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]
    
    def get_queryset(self):
        user = self.request.user
        return HustleListing.objects.filter(university=user.studentprofile.university, is_deleted=False)

    def perform_create(self, serializer):
        # Automatically assign the university based on the user's profile
        serializer.save(university=self.request.user.studentprofile.university)

class HustleListingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HustleListingSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        return HustleListing.objects.filter(university=user.studentprofile.university, is_deleted=False)

# Event Views
class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]

    def get_queryset(self):
        return Event.objects.filter(university=self.request.user.studentprofile.university, is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(university=self.request.user.studentprofile.university)

class EventRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Event.objects.filter(university=self.request.user.studentprofile.university, is_deleted=False)

# Event Listing Views
class EventListingListCreateView(generics.ListCreateAPIView):
    serializer_class = EventListingSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]

    def get_queryset(self):
        return EventListing.objects.filter(university=self.request.user.studentprofile.university, is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(university=self.request.user.studentprofile.university)
        
class EventListingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventListingSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return EventListing.objects.filter(university=self.request.user.studentprofile.university, is_deleted=False)