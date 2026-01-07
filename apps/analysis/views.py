from rest_framework import generics, viewsets

from .models import Analysis
from .serializers import AnalysisSerializer


class AnalysisViewSet(viewsets.ModelViewSet):
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer


class AnalysisListView(generics.ListAPIView):
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        queryset = Analysis.objects.all()
        if self.request.user and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        period_type = self.request.query_params.get("type")
        if period_type:
            queryset = queryset.filter(type=period_type)
        return queryset
