from django.urls import path
from . import views

urlpatterns = [
    path('organizations/', views.OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('organizations/<slug:slug>/', views.OrganizationRetrieveUpdateDestroyView.as_view(), name='organization-detail'),

    path('categories/', views.CategoryListView.as_view(), name='category-list'),

    path('hustles/', views.HustleListingListCreateView.as_view(), name='hustle-list-create'),
    path('hustles/<slug:slug>/', views.HustleListingRetrieveUpdateDestroyView.as_view(), name='hustle-detail'),

    path('events/', views.EventListCreateView.as_view(), name='event-list-create'),
    path('events/<slug:slug>/', views.EventRetrieveUpdateDestroyView.as_view(), name='event-detail'),

    path('event-listings/', views.EventListingListCreateView.as_view(), name='event-listing-list-create'),
    path('event-listings/<slug:slug>/', views.EventListingRetrieveUpdateDestroyView.as_view(), name='event-listing-detail'),
]