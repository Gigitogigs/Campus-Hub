from django.urls import path
from . import views

urlpatterns = [
    path('hustlers/', views.hustle_list, name='hustle_list'),
]