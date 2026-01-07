from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/analysis/", include("apps.analysis.urls")),
    path("api/notification/", include("apps.notification.urls")),
    path("api/accounts/", include("apps.account.urls")),
    path("api/transactions/", include("apps.transaction.urls")),
]

# django-debug-toolbar URL 추가 (개발 환경에서만)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

