from rest_framework import generics, permissions
from .models import Report
from .serializers import ReportCreateSerializer
from apps.market_hub.permissions import HasStudentProfile

class CreateReportView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated, HasStudentProfile]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)