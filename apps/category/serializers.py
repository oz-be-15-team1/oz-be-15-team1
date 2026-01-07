from rest_framework import serializers
from .models import Category


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "kind", "sort_order", "parent"]
        read_only_fields = ["id"]


class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "kind", "sort_order", "parent", "created_at"]
