from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

#import my models
from .models import HustleListing, Organization
from .serializers import HustleListingSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def hustle_list(request):
    """
    Handles listing all hustles
    """
    #===SCENARIO 1: USER wants to SEE items===
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return Response({"detail": "Please log in to see campus items."}, status=403)#if not logged in
        
        user_university = request.user.studentprofile.university #identify the university
        listings = HustleListing.objects.filter(university=user_university, is_deleted=False)#query the Db
        serializer = HustleListingSerializer(listings, many =True)#convet to JSON
        return Response(serializer.data)
    
    # ===SCENARIO 2: USER wants to POST an item===
    elif request.method == 'POST':      #Check if they have an Organization
        try:
            user_org = Organization.objects.get(owner=request.user)
        except Organization.DoesNotExist:
            return Response(
                {"error": "You need to create a Business or Club profile first"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if serializer.is_valid():       #Validate
            serializer.save(
                university=request.user.studentprofile.university,
                organization=user_org
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)