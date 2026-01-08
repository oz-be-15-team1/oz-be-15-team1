from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Notification 모델 직렬화.
    """

    class Meta:
        model = Notification
        fields = "__all__"
