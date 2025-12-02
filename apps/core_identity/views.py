from django.shortcuts import render
from .serializers import UserSerializer, StudentProfileSerializer, UniversitySerializer
from .models import User, StudentProfile, EmailVerification, University
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView


# Create your views here.
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to register
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # The serializer's validation will automatically check if the email is unique.
        # If it's not unique, it will raise a validation error, so we don't need to check manually.

        # Use perform_create which is the standard way in CreateAPIView. It calls serializer.save().
        user = serializer.save()

        # --- OTP and Email Verification Logic ---
        # 1. Generate a 6-digit OTP
        otp_code = str(random.randint(100000, 999999))

        # 2. Save the OTP to the database, linked to the user
        # Use update_or_create to handle cases where an unverified user tries to register again.
        EmailVerification.objects.update_or_create(
            user=user,
            defaults={'otp_code': otp_code}
        )

        # 3. Send the OTP to the user's email
        # Make sure you have configured your email settings in settings.py
        send_mail(
            subject='Your Campus Hub Verification Code',
            message=f'Welcome to Campus Hub! Your OTP code is: {otp_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # Return a success response
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Registration successful. Please check your email for an OTP to verify your account."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class StudentProfileCreateView(generics.CreateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Check if the user already has a student profile
        if StudentProfile.objects.filter(user=request.user).exists():
            return Response(
                {"error": "A student profile for this user already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # --- University Email Domain Validation ---
        # Get the university slug from the request data
        university_slug = request.data.get('university')
        if not university_slug:
            return Response({"error": "University is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            university = University.objects.get(slug=university_slug)
        except University.DoesNotExist:
            return Response({"error": "Invalid university selected."}, status=status.HTTP_400_BAD_REQUEST)

        user_email_domain = request.user.email.split('@')[-1]

        if user_email_domain not in university.allowed_domains:
            return Response(
                {"error": f"Your email domain ('{user_email_domain}') is not allowed for {university.name}. Please register with a valid student email."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # --- End Validation ---

        # If no profile exists, proceed with creation
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class StudentProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        #ensures the user can only return their own profile
        return self.request.user.studentprofile
        
class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        if not email or not otp_code:
            return Response({'error': 'Email and OTP code are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            verification = EmailVerification.objects.get(user__email=email, otp_code=otp_code)
            if verification.is_expired():
                return Response({'error': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = verification.user
            user.is_verified = True
            user.save()
            
            #OTP is used 
            verification.delete()
            
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        
        except EmailVerification.DoesNotExist:
            return Response({'error': 'Invalid OTP code.'}, status=status.HTTP_400_BAD_REQUEST)
        
class UserLoginView(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        # The default serializer expects 'username', but we use 'email'.
        # We pass the email from the request as the username to the serializer.
        login_data = request.data.copy()
        login_data['username'] = request.data.get('email')
        serializer = self.get_serializer(data=login_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        if not user.is_verified:
            return Response(
                {'error': 'Please verify your email before logging in.'}
                , status=status.HTTP_403_FORBIDDEN
            )
            
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
        
        
class UniversityListView(generics.ListAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.AllowAny] #List is public
    