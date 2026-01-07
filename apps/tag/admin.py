from django.contrib import admin

from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "color", "deleted_at", "created_at")
    list_filter = ("deleted_at",)
    search_fields = ("name",)
