from django.urls import path
from . import views

urlpatterns=[
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('verify-email/', views.EmailVerificationView.as_view(), name='email-verify'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    # Profile and University
    path('profile/', views.StudentProfileCreateView.as_view(), name='profile-create'),
    path('profile/me/', views.StudentProfileRetrieveUpdateView.as_view(), name='profile-detail'),
    path('universities/', views.UniversityListView.as_view(), name='university-list'),
]