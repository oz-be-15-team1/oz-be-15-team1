
from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "kind", "parent", "deleted_at", "created_at")
    list_filter = ("kind", "deleted_at")
    search_fields = ("name",)
