from rest_framework.routers import DefaultRouter

from .views import AccountViewSet

router = DefaultRouter()

# 계좌 관련 엔드포인트 등록
router.register(r"", AccountViewSet, basename="accounts")

urlpatterns = router.urls
