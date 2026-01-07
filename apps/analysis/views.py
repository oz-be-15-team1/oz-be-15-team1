from rest_framework import viewsets

from .models import Analysis
from .serializers import AnalysisSerializer


class AnalysisViewSet(viewsets.ModelViewSet):
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer
