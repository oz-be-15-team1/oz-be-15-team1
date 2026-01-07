from rest_framework.routers import DefaultRouter

# TransactionViewSet을 임포트
from .views import TransactionViewSet

# 라우터 인스턴스를 생성
router = DefaultRouter()

# 거래 관련 엔드포인트 등록
router.register(r"", TransactionViewSet, basename="transactions")

# 라우터에서 생성된 URL 패턴을 노출
urlpatterns = router.urls
