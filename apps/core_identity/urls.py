from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns=[
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('verify-email/', views.EmailVerificationView.as_view(), name='email-verify'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # Profile and University
    path('profile/', views.StudentProfileCreateView.as_view(), name='profile-create'),
    path('profile/me/', views.StudentProfileRetrieveUpdateView.as_view(), name='profile-detail'),
    path('universities/', views.UniversityListView.as_view(), name='university-list'),
]