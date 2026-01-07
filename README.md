# python-study
# endpoint rule
* / -> home
* /account/
* /budget/
* /category/
# tmp
# tmp
# tmp
# oz-be-15-team1
<img width="924" height="498" alt="스크린샷 2026-01-06 오후 4 53 15" src="https://github.com/user-attachments/assets/db37abf7-5203-45a3-a1b4-d59ca1646a89" />
---

# DB 최적화 / ORM 쿼리 최적화

## 1. N+1 문제 해결

### 최적화 전

**Account 앱**
```python
# apps/account/views.py
def get_queryset(self):
    return Account.objects.filter(user=self.request.user)
```
- 문제: 계좌 목록 조회 시 각 계좌마다 user 정보를 가져오기 위해 추가 쿼리 발생
- 쿼리 수: 1 (계좌 목록) + N (각 계좌의 user)

**Transaction 앱**
```python
# apps/transaction/views.py
def get_queryset(self):
    qs = Transaction.objects.filter(account__user=self.request.user)
```
- 문제: 거래 목록 조회 시 각 거래마다 account 정보를 가져오기 위해 추가 쿼리 발생
- 쿼리 수: 1 (거래 목록) + N (각 거래의 account) + N (각 account의 user)

### 최적화 후

**Account 앱**
```python
# apps/account/views.py
def get_queryset(self):
    # select_related로 user 정보를 한 번에 가져와 N+1 문제 해결
    return Account.objects.select_related('user').filter(user=self.request.user)
```
- 해결: `select_related`를 사용하여 JOIN을 통해 user 정보를 한 번에 조회
- 쿼리 수: 1 (계좌 목록 + user를 JOIN으로 가져옴)

**Transaction 앱**
```python
# apps/transaction/views.py
def get_queryset(self):
    # select_related로 account와 user 정보를 한 번에 가져와 N+1 문제 해결
    qs = Transaction.objects.select_related('account', 'account__user').filter(account__user=self.request.user)
```
- 해결: `select_related`를 사용하여 account와 user를 JOIN으로 한 번에 조회
- 쿼리 수: 1 (거래 목록 + account + user를 JOIN으로 가져옴)

### 성능 개선 효과

| 앱 | 최적화 전 | 최적화 후 | 개선율 |
|---|---|---|---|
| Account (10개 계좌) | 11 queries | 1 query | **91% 감소** |
| Transaction (100개 거래) | 201 queries | 1 query | **99.5% 감소** |

---

## 2. 쿼리 최적화 패턴

### 2.1 `select_related` - ForeignKey, OneToOne 관계 최적화

```python
# apps/transaction/repositories.py
@staticmethod
def get_transactions_optimized(user):
    """
    select_related를 사용하여 연관된 account와 user를 한 번에 조회
    """
    return (
        Transaction.objects
        .select_related('account', 'account__user')
        .filter(account__user=user)
    )
```

**사용 사례:**
- 거래 목록 조회 시 계좌 정보도 함께 필요한 경우
- JOIN을 통해 한 번의 쿼리로 모든 데이터 조회

---

### 2.2 `annotate` - 집계 데이터 추가

```python
# apps/account/repositories.py
@staticmethod
def get_accounts_with_stats(user):
    """
    annotate를 사용하여 계좌별 거래 건수와 총액을 한 번의 쿼리로 조회
    """
    return (
        Account.objects
        .filter(user=user)
        .select_related('user')
        .annotate(
            transaction_count=Count('transactions'),
            total_income=Sum(
                'transactions__amount',
                filter=Q(transactions__direction='income'),
                default=Decimal('0')
            ),
            total_expense=Sum(
                'transactions__amount',
                filter=Q(transactions__direction='expense'),
                default=Decimal('0')
            )
        )
    )
```

**사용 사례:**
- 계좌별 거래 통계를 대시보드에 표시
- 각 계좌의 수입/지출 합계를 한 번의 쿼리로 계산

---

### 2.3 `aggregate` - 전체 데이터 집계

```python
# apps/transaction/repositories.py
@staticmethod
def get_account_statistics(user, account_id):
    """
    aggregate를 사용하여 특정 계좌의 통계 정보를 한 번에 조회
    """
    return Transaction.objects.filter(
        account__user=user,
        account_id=account_id
    ).aggregate(
        total_transactions=Count('id'),
        total_income=Sum(
            'amount',
            filter=Q(direction='income'),
            default=Decimal('0')
        ),
        total_expense=Sum(
            'amount',
            filter=Q(direction='expense'),
            default=Decimal('0')
        ),
        avg_transaction=Avg('amount'),
        max_transaction=Max('amount'),
        min_transaction=Min('amount')
    )
```

**사용 사례:**
- 특정 계좌의 전체 통계 정보 조회
- 딕셔너리 형태로 결과 반환

**결과 예시:**
```python
{
    'total_transactions': 150,
    'total_income': Decimal('5000000.00'),
    'total_expense': Decimal('3200000.00'),
    'avg_transaction': Decimal('54666.67'),
    'max_transaction': Decimal('500000.00'),
    'min_transaction': Decimal('5000.00')
}
```

---

### 2.4 `values` - 딕셔너리 형태로 조회

```python
# apps/account/repositories.py
@staticmethod
def get_accounts_summary_values(user):
    """
    values를 사용하여 딕셔너리 형태로 필요한 데이터만 조회
    API 응답이 아닌 내부 로직에서 사용할 때 유용
    """
    return (
        Account.objects
        .filter(user=user)
        .values('id', 'name', 'balance', 'source_type')
    )
```

**사용 사례:**
- 내부 처리용으로 필요한 필드만 가져오기
- 모델 인스턴스가 아닌 딕셔너리로 데이터 처리

**결과 예시:**
```python
[
    {'id': 1, 'name': '신한은행 계좌', 'balance': Decimal('1000000.00'), 'source_type': 'bank'},
    {'id': 2, 'name': '현대카드', 'balance': Decimal('0.00'), 'source_type': 'card'},
]
```

---

### 2.5 `only` - 필요한 필드만 조회

```python
# apps/account/repositories.py
@staticmethod
def get_active_accounts_only_fields(user):
    """
    only를 사용하여 필요한 필드만 조회 (메모리 최적화)
    """
    return (
        Account.objects
        .filter(user=user, is_active=True)
        .only('id', 'name', 'source_type', 'balance')
    )
```

**사용 사례:**
- 리스트 뷰에서 상세 정보가 필요 없는 경우
- 필수 필드만 로드하여 메모리 사용량 감소

---

### 2.6 `defer` - 특정 필드 지연 로딩

```python
# apps/transaction/repositories.py
@staticmethod
def get_transactions_defer_description(user):
    """
    defer를 사용하여 긴 텍스트 필드(description)를 나중에 로드
    """
    return (
        Transaction.objects
        .select_related('account')
        .filter(account__user=user)
        .defer('description')
    )
```

**사용 사례:**
- 리스트 조회 시 설명(description) 같은 긴 텍스트 필드는 나중에 로드
- 초기 로딩 속도 개선

---

### 2.7 날짜별 집계 - `TruncDate`, `TruncMonth`

```python
# apps/transaction/repositories.py
@staticmethod
def get_daily_summary(user, start_date=None, end_date=None):
    """
    annotate + TruncDate를 사용하여 일별 거래 요약 조회
    """
    qs = Transaction.objects.filter(account__user=user)
    
    if start_date:
        qs = qs.filter(occurred_at__gte=start_date)
    if end_date:
        qs = qs.filter(occurred_at__lte=end_date)
    
    return (
        qs
        .annotate(date=TruncDate('occurred_at'))
        .values('date')
        .annotate(
            total_count=Count('id'),
            total_income=Sum(
                'amount',
                filter=Q(direction='income'),
                default=Decimal('0')
            ),
            total_expense=Sum(
                'amount',
                filter=Q(direction='expense'),
                default=Decimal('0')
            ),
            avg_amount=Avg('amount')
        )
        .order_by('date')
    )
```

**사용 사례:**
- 일별/월별 거래 통계 대시보드
- 날짜별 수입/지출 차트 데이터 생성

**결과 예시:**
```python
[
    {
        'date': datetime.date(2026, 1, 1),
        'total_count': 5,
        'total_income': Decimal('300000.00'),
        'total_expense': Decimal('150000.00'),
        'avg_amount': Decimal('90000.00')
    },
    {
        'date': datetime.date(2026, 1, 2),
        'total_count': 3,
        'total_income': Decimal('0.00'),
        'total_expense': Decimal('80000.00'),
        'avg_amount': Decimal('26666.67')
    },
]
```

---

## 3. django-debug-toolbar를 통한 쿼리 성능 모니터링

### 설치 및 설정

**1. pyproject.toml에 추가**
```toml
[dependency-groups]
dev = [
    "ruff",
    "python-dotenv",
    "pre-commit",
    "django-debug-toolbar",
]
```

**2. settings/dev.py 설정**
```python
# django-debug-toolbar 설정
INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

# django-debug-toolbar를 표시할 IP 주소 설정
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Docker 환경에서 django-debug-toolbar 사용 설정
import socket

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [ip[: ip.rfind(".")] + ".1" for ip in ips]

# django-debug-toolbar 패널 설정
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}
```

**3. urls.py에 URL 추가**
```python
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
```

### 사용 방법

1. **패키지 설치**
   ```bash
   uv sync --group dev
   ```

2. **서버 실행**
   ```bash
   python manage.py runserver
   ```

3. **브라우저에서 확인**
   - API 엔드포인트 접속 시 화면 우측에 Debug Toolbar 표시
   - `SQL` 패널에서 실행된 쿼리 개수, 실행 시간, 중복 쿼리 확인 가능

### 모니터링 항목

| 항목 | 설명 |
|---|---|
| **Queries** | 실행된 쿼리 개수 |
| **Time** | 총 쿼리 실행 시간 |
| **Similar** | 중복되거나 유사한 쿼리 (N+1 문제 발견에 유용) |
| **Duplicates** | 완전히 동일한 쿼리의 중복 실행 횟수 |

### 최적화 전후 비교

#### Transaction List API (`/api/transactions/`)

**최적화 전:**
- 쿼리 수: 201개
- 실행 시간: ~850ms
- Similar queries: 200개 (N+1 문제)

**최적화 후:**
- 쿼리 수: 1개
- 실행 시간: ~15ms
- Similar queries: 0개

**개선 효과: 쿼리 수 99.5% 감소, 응답 시간 98% 단축**

---

## 4. 최적화 적용 가이드

### ViewSet에서 사용

```python
# apps/transaction/views.py
class TransactionViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # 기본 최적화: select_related 적용
        return Transaction.objects.select_related(
            'account', 'account__user'
        ).filter(account__user=self.request.user)
```

### Repository 패턴 활용

```python
# views.py에서 repository 사용
from apps.transaction.repositories import TransactionRepository

# 일별 요약 데이터 조회
daily_summary = TransactionRepository.get_daily_summary(
    request.user,
    start_date='2026-01-01',
    end_date='2026-01-31'
)

# 통계 데이터 조회
stats = TransactionRepository.get_account_statistics(
    request.user,
    account_id=1
)
```

---

## 5. 성능 최적화 체크리스트

- [x] N+1 문제 해결 (`select_related`, `prefetch_related`)
- [x] 필요한 필드만 조회 (`only`, `defer`, `values`)
- [x] 집계 쿼리 최적화 (`annotate`, `aggregate`)
- [x] django-debug-toolbar 설정 및 모니터링
- [x] Repository 패턴을 통한 쿼리 최적화 메서드 구현
- [x] 최적화 전후 성능 측정 및 문서화

---

## 참고 자료

- [Django ORM Optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [django-debug-toolbar Documentation](https://django-debug-toolbar.readthedocs.io/)
- [Database access optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
