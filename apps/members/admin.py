from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # 관리자 화면에 표시할 필드
    list_display = ("email", "name", "phone", "is_staff", "is_active")
    
    # 검색 기능
    search_fields = ("email", "name", "phone")
    
    # is_staff와 is_active를 기준으로 유저를 필터링
    list_filter = ("is_staff", "is_active")
    
    # 읽기 전용 필드 설정
    readonly_fields = ("is_staff",)  # 어드민 권한은 읽기 전용
    
    # 기본 UserAdmin에서 제공하는 필드셋 사용 가능
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "phone")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),   # 계정의 권한 수정 가능
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    filter_horizontal = ("groups", "user_permissions")  # filter_horizontal은 PermissionsMixin 상속 후에만 가능
    ordering = ("email",)

    def get_readonly_fields(self, request, obj=None):
        # 슈퍼유저는 모든 필드 수정 가능
        if request.user.is_superuser:
            return ()
        return self.readonly_fields  # 일반 어드민은 readonly_fields 적용