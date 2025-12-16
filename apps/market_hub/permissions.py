from rest_framework.permissions import BasePermission
from rest_framework import permissions
from apps.core_identity.models import StudentProfile

class HasStudentProfile(BasePermission):
    """
    Allows access only to users who have a student profile.
    """
    message = 'A student profile is required to perform this action.'

    def has_permission(self, request, view):
        return hasattr(request.user, 'studentprofile') and request.user.studentprofile is not None
    
class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        #Read permissions are allowed to any request,
        #we'll allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        #Instance must have attribute "owner"
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'organization'):
            return obj.organization.owner == request.user
        
        return False