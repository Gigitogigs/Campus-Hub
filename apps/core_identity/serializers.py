from .models import User, StudentProfile, University
from rest_framework import serializers
import uuid

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'is_verified')
        read_only_fields = ('id', 'is_verified')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Automatically set a unique username and create the user
        validated_data['username'] = f"user_{uuid.uuid4().hex[:10]}"
        user = User.objects.create_user(**validated_data)
        return user

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ('university', 'course', 'year_of_study', 'phone_number')
        
class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ('name', 'slug')
