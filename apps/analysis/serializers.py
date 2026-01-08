from rest_framework import serializers

from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    """
    Analysis 모델 직렬화.
    """

    class Meta:
        model = Analysis
        fields = "__all__"
