import io
from PIL import Image as PilImage
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from apps.core_identity.models import User, University, StudentProfile
from .models import Category, Organization, HustleListing, Event, EventListing

class MarketHubAPITests(APITestCase):
    """
    Test suite for the market_hub app API endpoints.
    """

    def setUp(self):
        """Set up initial data for tests."""
        self.university = University.objects.create(name='Market University', slug='market-university', allowed_domains=['test.edu'])
        
        # User WITH a student profile
        self.profiled_user = User.objects.create_user(email='profiled@test.edu', password='password123', is_verified=True)
        self.profile = StudentProfile.objects.create(
            user=self.profiled_user,
            university=self.university,
            course='Business',
            year_of_study=2
        )

        # User WITHOUT a student profile
        self.unprofiled_user = User.objects.create_user(email='unprofiled@test.edu', password='password123', is_verified=True)

        self.hustles_url = reverse('hustle-list-create')
        self.orgs_url = reverse('organization-list-create')
        self.category = Category.objects.create(name='Electronics', cat_type='HUSTLE', icon='url.com/icon')
        self.event_category = Category.objects.create(name='Concert', cat_type='EVENT', icon='url.com/icon')
        self.events_url = reverse('event-list-create')
        self.event_listings_url = reverse('event-listing-list-create')

        # Create a default organization for the profiled user to use in tests
        self.organization = Organization.objects.create(
            owner=self.profiled_user,
            university=self.university,
            name='Test Shop',
            org_type='BUSINESS'
        )
        
        # Create another user (User B) for permission tests
        self.other_user = User.objects.create_user(email='other@test.edu', password='password123', is_verified=True)
        self.other_profile = StudentProfile.objects.create(
            user=self.other_user,
            university=self.university,
            course='Arts',
            year_of_study=1
        )
        self.other_organization = Organization.objects.create(
            owner=self.other_user,
            university=self.university,
            name='Other Shop',
            org_type='BUSINESS'
        )

    # --- Permission Tests ---
    def test_access_denied_for_user_without_profile(self):
        """
        Ensure users without a student profile get a 403 Forbidden error.
        """
        self.client.force_authenticate(user=self.unprofiled_user)
        response = self.client.get(self.hustles_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'A student profile is required to perform this action.')

    def test_access_granted_for_user_with_profile(self):
        """
        Ensure users with a student profile can access the endpoint.
        """
        self.client.force_authenticate(user=self.profiled_user)
        response = self.client.get(self.hustles_url)
        # We expect 200 OK because access is granted, even if the list is empty.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Organization Tests ---
    def test_create_organization_success(self):
        """
        Ensure a user with a profile can create an organization.
        """
        self.client.force_authenticate(user=self.profiled_user)
        org_data = {
            'name': 'Student Tech Club',
            'org_type': 'CLUB',
            'whatsapp_number': '+254700000000'
        }
        response = self.client.post(self.orgs_url, org_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Organization.objects.count(), 3)
        # Verify owner and university were set automatically
        self.assertEqual(response.data['owner'], self.profiled_user.id)
        self.assertEqual(response.data['university'], self.university.id)

    # --- Hustle Listing Tests ---
    def test_create_hustle_listing_success(self):
        """
        Ensure a user with a profile can create a hustle listing.
        """
        self.client.force_authenticate(user=self.profiled_user)
        
        hustle_data = {
            'title': 'Slightly Used Laptop',
            'price': '50000.00',
            'description': 'A great laptop for students.',
            'category': self.category.name,
            'organization': self.organization.name
        }

        response = self.client.post(self.hustles_url, hustle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify the university was set automatically by perform_create
        self.assertEqual(response.data['university'], self.university.id)
        self.assertEqual(HustleListing.objects.count(), 1)

    def test_retrieve_hustle_listing_by_slug(self):
        """
        Ensure a single hustle listing can be retrieved by its slug.
        """
        hustle = HustleListing.objects.create(
            organization=self.organization,
            university=self.university,
            category=self.category,
            title='Unique Test Item',
            price='123.45'
        )
        self.assertEqual(HustleListing.objects.count(), 1)
        detail_url = reverse('hustle-detail', kwargs={'slug': hustle.slug})
        self.client.force_authenticate(user=self.profiled_user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Unique Test Item')

    def test_update_hustle_listing_success(self):
        """
        Ensure a user can update their own hustle listing.
        """
        hustle = HustleListing.objects.create(
            organization=self.organization,
            university=self.university,
            category=self.category,
            title='Original Title',
            price='100.00'
        )
        detail_url = reverse('hustle-detail', kwargs={'slug': hustle.slug})
        update_data = {'title': 'Updated Title', 'price': '150.00'}
        self.client.force_authenticate(user=self.profiled_user)
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertEqual(response.data['price'], '150.00')

    def test_update_others_hustle_listing_forbidden(self):
        """
        Ensure a user cannot update a hustle listing belonging to another user's organization.
        """
        # Create a listing for User B's organization
        hustle = HustleListing.objects.create(
            organization=self.other_organization,
            university=self.university,
            category=self.category,
            title='User B Item',
            price='200.00'
        )
        
        detail_url = reverse('hustle-detail', kwargs={'slug': hustle.slug})
        update_data = {'title': 'Hacked Title'}
        
        # Authenticate as User A (self.profiled_user)
        self.client.force_authenticate(user=self.profiled_user)
        response = self.client.patch(detail_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_others_organization_forbidden(self):
        """
        Ensure a user cannot update another user's organization.
        """
        url = reverse('organization-detail', kwargs={'slug': self.other_organization.slug})
        update_data = {'name': 'Hacked Org Name'}
        
        self.client.force_authenticate(user=self.profiled_user)
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_others_organization_forbidden(self):
        """
        Ensure a user cannot delete another user's organization.
        """
        url = reverse('organization-detail', kwargs={'slug': self.other_organization.slug})
        self.client.force_authenticate(user=self.profiled_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Event Tests ---
    def test_create_event_success(self):
        """
        Ensure a user can create an event with an image.
        """
        self.client.force_authenticate(user=self.profiled_user)
        
        # Create a dummy image file
        file = io.BytesIO()
        image = PilImage.new('RGB', (100, 100), 'white')
        image.save(file, 'JPEG')
        file.seek(0)
        image_file = SimpleUploadedFile("test_event.jpg", file.read(), content_type="image/jpeg")
        
        event_data = {
            'title': 'Campus Music Fest',
            'category': self.event_category.name,
            'organization': self.organization.name,
            'date_time': '2023-12-25T18:00:00Z',
            'location': 'Main Hall',
            'description': 'A night of music and fun.',
            'image': image_file
        }

        # Use multipart format for file uploads
        response = self.client.post(self.events_url, event_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(response.data['university'], self.university.id)

    def test_retrieve_event_by_slug(self):
        """
        Ensure an event can be retrieved by its slug.
        """
        event = Event.objects.create(
            organization=self.organization,
            university=self.university,
            title='Art Exhibition',
            category=self.event_category,
            date_time='2023-11-20T10:00:00Z',
            location='Art Gallery',
            description='Showcasing student art.',
            image='events/test.jpg'
        )
        
        url = reverse('event-detail', kwargs={'slug': event.slug})
        self.client.force_authenticate(user=self.profiled_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Art Exhibition')

    # --- Event Listing Tests ---
    def test_create_event_listing_success(self):
        """
        Ensure a user can create an event listing linked to an event.
        """
        # First create the parent event
        event = Event.objects.create(
            organization=self.organization,
            university=self.university,
            title='Tech Talk',
            category=self.event_category,
            date_time='2023-11-20T10:00:00Z',
            location='Auditorium',
            description='Talk about tech.',
            image='events/tech.jpg'
        )

        self.client.force_authenticate(user=self.profiled_user)
        
        data = {
            'title': 'Tech Talk Tickets',
            'organization': self.organization.name,
            'event': event.slug,  # Linking via slug
            'description': 'Get your tickets here.'
        }

        response = self.client.post(self.event_listings_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EventListing.objects.count(), 1)
        
        # Verify the relationship
        created_listing = EventListing.objects.get()
        self.assertEqual(created_listing.event, event)
        self.assertEqual(created_listing.university, self.university)
