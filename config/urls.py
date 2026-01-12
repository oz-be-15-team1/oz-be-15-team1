from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# SWAGGER: API 문서화 라이브러리
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# SWAGGER: Schema View 설정
schema_view = get_schema_view(
    openapi.Info(
        title="Budget API",
        default_version="v1",
        description="예산 관리 시스템 API - 사용자 계정, 거래, 카테고리, 태그, 분석 등을 관리합니다.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@budget.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # allauth (소셜 로그인)
    path("allauth/", include("allauth.urls")),
    # SWAGGER: API 문서 UI 엔드포인트
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # API 엔드포인트
    path("api/analyses/", include("apps.analysis.urls")),
    path("api/notifications/", include("apps.notification.urls")),
    path("api/accounts/", include("apps.bank_account.urls")),
    path("api/transactions/", include("apps.transaction.urls")),
    path("api/users/", include("apps.members.urls")),
    path("api/categories/", include("apps.category.urls")),
    path("api/tags/", include("apps.tag.urls")),
]

# django-debug-toolbar URL 추가 (개발 환경에서만)
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
