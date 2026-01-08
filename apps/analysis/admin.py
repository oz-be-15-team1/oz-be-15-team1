from django.contrib import admin

from .models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    """
    Analysis 어드민 설정.
    """

    list_display = ["user", "about", "type", "period_start", "period_end", "created_at"]
    list_filter = ["type", "about", "created_at"]
    search_fields = ["user__email", "description"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
