from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["user__email", "message"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
    actions = ["mark_as_read", "mark_as_unread"]

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()}개의 알림을 읽음으로 표시했습니다.")

    mark_as_read.short_description = "선택된 알림을 읽음으로 표시"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()}개의 알림을 읽지 않음으로 표시했습니다.")

    mark_as_unread.short_description = "선택된 알림을 읽지 않음으로 표시"
