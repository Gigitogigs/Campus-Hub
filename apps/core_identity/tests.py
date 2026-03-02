# Test file for core_identity app
from django.test import TestCase
from .models import User, StudentProfile, EmailVerification, University
from django.core import mail
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

class CoreIdentityAPITests(APITestCase):
    
    def setUp(self):
        self.university = University.objects.create(name='Test University',
                                                    slug='test-university',
                                                    allowed_domains=['test.edu']
                                                    )
        self.register_url = reverse('user-register')
        self.verify_url = reverse('email-verify')
        self.login_url = reverse('user-login')
        self.profile_create_url = reverse('profile-create')
        self.profile_detail_url = reverse('profile-detail')
        
        self.user_data = {
            'email': 'testuser@test.edu',
            'password': 'testpassword'
        }
        
        #Registration Tests
    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'testuser@test.edu')
        #check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your Campus Hub Verification Code')
        
    def test_user_registration_duplicate_email(self):
        User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
        #Email Verification Tests
    def test_email_verification_success(self):
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        otp = '123456'
        EmailVerification.objects.create(user=user, otp_code=otp)
        
        response = self.client.post(self.verify_url, {'email': user.email, 'otp_code': otp}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        #check otp deletion after use
        self.assertFalse(EmailVerification.objects.filter(user=user).exists())
        
    def test_email_verification_invalid_otp(self):
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        EmailVerification.objects.create(user=user, otp_code='123456')
        
        response = self.client.post(self.verify_url, {'email': user.email, 'otp_code': '141343'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_verified)
        
    def test_email_verification_expired_otp(self):
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        otp_record = EmailVerification.objects.create(user=user, otp_code='123456')
        #manually set the creation date to be in the past
        otp_record.created_at = timezone.now() - timedelta(minutes=15)
        otp_record.save()
        
        response = self.client.post(self.verify_url, {'email': user.email, 'otp_code': '123456'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('OTP has expired.', response.data['error'])
        
        #login Tests
        
    def test_login_unverified_user(self):
        User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_login_verified_user_success(self):
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        user.is_verified = True
        user.save()
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert the new JWT pair keys are present
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        #Profile Creation Tests
    def test_create_student_profile_success(self):
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'], is_verified=True)
        self.client.force_authenticate(user=user)
        profile_data = {'university': self.university.slug,
                        'course': 'Computer Science',
                        'year_of_study': 3
                        }
        response = self.client.post(self.profile_create_url, profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())
        self.assertEqual(user.studentprofile.course, 'Computer Science')
        
    def test_create_profile_when_already_exists(self):
        """
        Ensure a user cannot create a second profile.
        """
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'], is_verified=True)
        StudentProfile.objects.create(user=user, university=self.university, course="Law", year_of_study=1)
        self.client.force_authenticate(user=user)

        profile_data = {'university': self.university.slug, 'course': 'Engineering', 'year_of_study': 2}
        response = self.client.post(self.profile_create_url, profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_and_update_own_profile(self):
        """
        Ensure a user can retrieve and update their own profile.
        """
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'], is_verified=True)
        StudentProfile.objects.create(user=user, university=self.university, course="Medicine", year_of_study=5)
        self.client.force_authenticate(user=user)

        # Retrieve
        response = self.client.get(self.profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course'], 'Medicine')

        # Update
        update_data = {'phone_number': '+254712345678'}
        response = self.client.patch(self.profile_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.studentprofile.refresh_from_db()
        self.assertEqual(user.studentprofile.phone_number, '+254712345678')
        
    def test_create_student_profile_with_invalid_email_domain(self):
        """
        Ensure a user cannot create a profile for a university with an unallowed email domain.
        """
        # This user's email domain is @gmail.com, which is not in the university's allowed_domains.
        user_with_invalid_email = User.objects.create_user(email='baduser@gmail.com', password='password123', is_verified=True)
        self.client.force_authenticate(user=user_with_invalid_email)

        profile_data = {
            'university': self.university.slug,
            'course': 'Invalid Course',
            'year_of_study': 1
        }
        response = self.client.post(self.profile_create_url, profile_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is not allowed for Test University", response.data['error'])
        self.assertFalse(StudentProfile.objects.filter(user=user_with_invalid_email).exists())


    # === JWT-Specific Tests ===

    def test_login_returns_jwt_pair(self):
        """Valid credentials for a verified user should return access and refresh tokens."""
        user = User.objects.create_user(email='jwt@test.edu', password='pass1234', is_verified=True)
        response = self.client.post(self.login_url, {'email': 'jwt@test.edu', 'password': 'pass1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user_id', response.data)

    def test_login_unverified_user_blocked(self):
        """An unverified user should be rejected with 403 before tokens are issued."""
        User.objects.create_user(email='unverified@test.edu', password='pass1234', is_verified=False)
        response = self.client.post(self.login_url, {'email': 'unverified@test.edu', 'password': 'pass1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_invalid_credentials(self):
        """Wrong password should return 401 Unauthorized."""
        User.objects.create_user(email='valid@test.edu', password='correct_password', is_verified=True)
        response = self.client.post(self.login_url, {'email': 'valid@test.edu', 'password': 'wrong_password'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_bearer_token(self):
        """A valid Bearer token should grant access to a protected endpoint."""
        user = User.objects.create_user(email='bearer@test.edu', password='pass1234', is_verified=True)
        StudentProfile.objects.create(user=user, university=self.university, course="CS", year_of_study=1)
        # Login to get the JWT
        login_response = self.client.post(self.login_url, {'email': 'bearer@test.edu', 'password': 'pass1234'}, format='json')
        access_token = login_response.data['access']
        # Use the JWT to access a protected route
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_refresh(self):
        """Posting a valid refresh token should return a new access token."""
        user = User.objects.create_user(email='refresh@test.edu', password='pass1234', is_verified=True)
        login_response = self.client.post(self.login_url, {'email': 'refresh@test.edu', 'password': 'pass1234'}, format='json')
        refresh_token = login_response.data['refresh']
        refresh_url = reverse('token-refresh')
        response = self.client.post(refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_throttling(self):
        """Exceeding the login rate limit (5/minute) should return 429 Too Many Requests."""
        User.objects.create_user(email='throttle@test.edu', password='pass1234', is_verified=True)
        data = {'email': 'throttle@test.edu', 'password': 'wrong'}
        for _ in range(5):
            self.client.post(self.login_url, data, format='json')
        # The 6th request should be throttled
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)