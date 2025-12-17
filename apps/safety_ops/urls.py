from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.CreateReportView.as_view(), name='create-report'),
]
#Frontend should send id not slug