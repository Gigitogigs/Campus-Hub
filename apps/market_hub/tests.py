from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.core_identity.models import User, University, StudentProfile
from .models import Category, Organization, HustleListing

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
        
        # Create a default organization for the profiled user to use in tests
        self.organization = Organization.objects.create(
            owner=self.profiled_user,
            university=self.university,
            name='Test Shop',
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
        self.assertEqual(Organization.objects.count(), 2)
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
