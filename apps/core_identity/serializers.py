from .models import User, StudentProfile, University
from rest_framework import serializers
import uuid

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for handling User registration.
    Converts incoming JSON to a User model, handling password hashing securely.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'is_verified')
        read_only_fields = ('id', 'is_verified')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Delegate user creation to the custom manager.
        # The manager will handle setting the username and hashing the password.
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the StudentProfile model.
    Handles reading/writing the user's specific campus context and linking them to a University.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    # For read operations, display the university's slug.
    # For write operations, look up the university by its 'id' (UUID).
    university = serializers.SlugRelatedField(
        queryset=University.objects.all(),
        slug_field='slug',
    )

    class Meta:
        model = StudentProfile
        fields = ('user', 'user_email', 'university', 'course', 'year_of_study', 'phone_number')
        read_only_fields = ('user',)
        
class UniversitySerializer(serializers.ModelSerializer):
    """
    Serializer for the University model.
    Provides basic read-only data for populating public selection lists.
    """
    class Meta:
        model = University
        fields = ('name', 'slug')
