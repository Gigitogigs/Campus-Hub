from rest_framework.permissions import BasePermission
from apps.core_identity.models import StudentProfile

class HasStudentProfile(BasePermission):
    """
    Allows access only to users who have a student profile.
    """
    message = 'A student profile is required to perform this action.'

    def has_permission(self, request, view):
        return hasattr(request.user, 'studentprofile') and request.user.studentprofile is not None