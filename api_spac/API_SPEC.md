# Budget API 스펙

Base URL: `/api`

인증:
- JWT 액세스 토큰을 `Authorization: Bearer <token>` 헤더로 전달
- 로그인 시 `refresh_token`이 HttpOnly 쿠키로 설정됨

Content-Type: `application/json`

## Users

### POST /api/users/signup/
회원가입.

요청 바디
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "홍길동",
  "phone": "010-1234-5678"
}
```

응답 바디 (201)
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "010-1234-5678"
}
```

상태 코드: 201, 400, 409

### POST /api/users/login/
로그인 및 JWT 액세스 토큰 발급.

요청 바디
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

응답 바디 (200)
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "홍길동",
    "phone": "010-1234-5678"
  },
  "token": "jwt-access-token"
}
```

상태 코드: 200, 400, 401

### POST /api/users/logout/
로그아웃 및 리프레시 토큰 무효화 (인증 필요).

요청 바디
```json
{
  "refresh": "jwt-refresh-token"
}
```

응답 바디 (200)
```json
{
  "detail": "Logout successful"
}
```

상태 코드: 200, 400, 401

### GET /api/users/profile/
내 프로필 조회 (인증 필요).

응답 바디 (200)
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "010-1234-5678"
}
```

상태 코드: 200, 401

### PATCH /api/users/profile/
내 프로필 수정 (인증 필요).

요청 바디
```json
{
  "name": "홍길동",
  "phone": "010-9999-0000"
}
```

응답 바디 (200)
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "010-9999-0000"
}
```

상태 코드: 200, 400, 401

### DELETE /api/users/profile/
내 계정 삭제 (인증 필요).

응답 바디 (200)
```json
{
  "detail": "Deleted successfully"
}
```

상태 코드: 200, 401

## Accounts

### GET /api/accounts/
계좌 목록 조회 (인증 필요).

응답 바디 (200)
```json
[
  {
    "id": 1,
    "name": "Main Bank",
    "source_type": "bank",
    "balance": "1000000.00",
    "is_active": true,
    "account_number": "110-123-456789",
    "account_type": "checking",
    "card_company": "",
    "card_number": "",
    "billing_day": null,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
  }
]
```

상태 코드: 200, 401

### POST /api/accounts/
계좌 생성 (인증 필요).

요청 바디
```json
{
  "name": "Main Bank",
  "source_type": "bank",
  "balance": "1000000.00",
  "account_number": "110-123-456789",
  "account_type": "checking",
  "card_company": "",
  "card_number": "",
  "billing_day": 25
}
```

응답 바디 (201)
```json
{
  "id": 1,
  "name": "Main Bank",
  "source_type": "bank",
  "balance": "1000000.00",
  "is_active": true,
  "account_number": "110-123-456789",
  "account_type": "checking",
  "card_company": "",
  "card_number": "",
  "billing_day": 25,
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T10:00:00Z"
}
```

상태 코드: 201, 400, 401

### GET /api/accounts/{id}/
계좌 상세 조회 (인증 필요).

응답 바디: 계좌 목록 항목과 동일.

상태 코드: 200, 401, 404

### DELETE /api/accounts/{id}/
계좌 삭제 (인증 필요).

응답 바디: 없음.

상태 코드: 204, 401, 404

참고: 계좌는 PUT/PATCH 수정 불가.

## Transactions

### GET /api/transactions/
거래 목록 조회 (인증 필요).

쿼리 파라미터:
- `account` (int)
- `direction` (income|expense|transfer)
- `min_amount` (number)
- `max_amount` (number)
- `start_date` (YYYY-MM-DD)
- `end_date` (YYYY-MM-DD)

응답 바디 (200)
```json
[
  {
    "id": 1,
    "account": 1,
    "account_name": "Main Bank",
    "amount": "50000.00",
    "balance_after": "950000.00",
    "direction": "expense",
    "method": "card",
    "description": "점심",
    "tags": [
      { "id": 1, "name": "고정지출", "color": "#3366FF", "created_at": "2026-01-08T10:00:00Z" }
    ],
    "occurred_at": "2026-01-08T12:30:00Z",
    "created_at": "2026-01-08T12:30:00Z",
    "updated_at": "2026-01-08T12:30:00Z"
  }
]
```

상태 코드: 200, 401

### POST /api/transactions/
거래 생성 (인증 필요).

요청 바디
```json
{
  "account": 1,
  "amount": "50000.00",
  "direction": "expense",
  "method": "card",
  "description": "점심",
  "occurred_at": "2026-01-08T12:30:00Z",
  "tags": [1, 2]
}
```

응답 바디 (201): 거래 목록 항목과 동일.

상태 코드: 201, 400, 401

### GET /api/transactions/{id}/
거래 상세 조회 (인증 필요).

응답 바디: 거래 목록 항목과 동일.

상태 코드: 200, 401, 404

### PATCH /api/transactions/{id}/
거래 수정 (인증 필요).

요청 바디 (부분 업데이트)
```json
{
  "amount": "60000.00",
  "description": "늦은 점심",
  "tags": [2]
}
```

응답 바디 (200): 거래 목록 항목과 동일.

상태 코드: 200, 400, 401, 404

### DELETE /api/transactions/{id}/
거래 삭제 (인증 필요).

응답 바디: 없음.

상태 코드: 204, 401, 404

참고: 거래는 PUT 전체 수정 불가.

## Categories

### GET /api/categories/
카테고리 목록 조회 (인증 필요).

응답 바디 (200)
```json
[
  {
    "id": 1,
    "name": "식비",
    "kind": "EXPENSE",
    "sort_order": 0,
    "parent": null,
    "created_at": "2026-01-08T10:00:00Z"
  }
]
```

상태 코드: 200, 401

### POST /api/categories/
카테고리 생성 (인증 필요).

요청 바디
```json
{
  "name": "식비",
  "kind": "EXPENSE",
  "sort_order": 0,
  "parent": null
}
```

응답 바디 (201): 카테고리 목록 항목과 동일.

상태 코드: 201, 400, 401

### GET /api/categories/{category_id}/
카테고리 상세 조회 (인증 필요).

응답 바디: 카테고리 목록 항목과 동일.

상태 코드: 200, 401, 404

### PATCH /api/categories/{category_id}/
카테고리 수정 (인증 필요).

요청 바디 (부분 업데이트)
```json
{
  "name": "외식비",
  "sort_order": 1
}
```

응답 바디 (200): 카테고리 목록 항목과 동일.

상태 코드: 200, 400, 401, 404

### DELETE /api/categories/{category_id}/
카테고리 삭제(소프트 삭제, 인증 필요).

응답 바디: 없음.

상태 코드: 204, 401, 404

### GET /api/categories/trash/
삭제된 카테고리 목록 조회 (인증 필요).

응답 바디: 카테고리 목록 항목과 동일.

상태 코드: 200, 401

### POST /api/categories/{category_id}/restore/
삭제된 카테고리 복구 (인증 필요).

응답 바디: 없음.

상태 코드: 200, 401, 404

## Tags

### GET /api/tags/
태그 목록 조회 (인증 필요).

응답 바디 (200)
```json
[
  {
    "id": 1,
    "name": "고정지출",
    "color": "#3366FF",
    "created_at": "2026-01-08T10:00:00Z"
  }
]
```

상태 코드: 200, 401

### POST /api/tags/
태그 생성 (인증 필요).

요청 바디
```json
{
  "name": "고정지출",
  "color": "#3366FF"
}
```

응답 바디 (201): 태그 목록 항목과 동일.

상태 코드: 201, 400, 401

### GET /api/tags/{tag_id}/
태그 상세 조회 (인증 필요).

응답 바디: 태그 목록 항목과 동일.

상태 코드: 200, 401, 404

### PATCH /api/tags/{tag_id}/
태그 수정 (인증 필요).

요청 바디 (부분 업데이트)
```json
{
  "name": "변동지출",
  "color": "#FF3366"
}
```

응답 바디 (200): 태그 목록 항목과 동일.

상태 코드: 200, 400, 401, 404

### DELETE /api/tags/{tag_id}/
태그 삭제(소프트 삭제, 인증 필요).

응답 바디: 없음.

상태 코드: 204, 401, 404

### GET /api/tags/trash/
삭제된 태그 목록 조회 (인증 필요).

응답 바디: 태그 목록 항목과 동일.

상태 코드: 200, 401

### POST /api/tags/{tag_id}/restore/
삭제된 태그 복구 (인증 필요).

응답 바디: 없음.

상태 코드: 200, 401, 404

## Analysis

### GET /api/analyses/
분석 목록 조회 (인증 필요).

응답 바디 (200)
```json
[
  {
    "id": 1,
    "user": 1,
    "about": "total_expense",
    "type": "monthly",
    "period_start": "2026-01-01",
    "period_end": "2026-01-31",
    "description": "월간 요약",
    "result_image": "/media/analysis_images/summary.png",
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
  }
]
```

상태 코드: 200, 401

### GET /api/analyses/{id}/
분석 상세 조회 (인증 필요).

응답 바디: 분석 목록 항목과 동일.

상태 코드: 200, 401, 404

### GET /api/analyses/period/
분석 목록 필터 조회 (인증 필요).

쿼리 파라미터:
- `type` (weekly|monthly)

응답 바디: 분석 목록 항목과 동일.

상태 코드: 200, 401

### POST /api/analyses/run/
분석 실행 요청 (인증 필요, 비동기).

요청 바디
```json
{
  "about": "total_expense",
  "type": "monthly",
  "period_start": "2026-01-01",
  "period_end": "2026-01-31"
}
```

응답 바디 (202)
```json
{
  "task_id": "celery-task-id"
}
```

상태 코드: 202, 400, 401

### GET /api/analyses/tasks/{task_id}/
분석 작업 상태 조회 (인증 필요).

응답 바디 (200)
```json
{
  "status": "PENDING",
  "result": null,
  "date_done": null
}
```

상태 코드: 200, 401

## Notifications

### GET /api/notifications/
알림 목록 조회 (인증 필요).

응답 바디 (200)
```json
[
  {
    "id": 1,
    "user": 1,
    "message": "예산 한도에 도달했습니다",
    "is_read": false,
    "created_at": "2026-01-08T10:00:00Z"
  }
]
```

상태 코드: 200, 401

### GET /api/notifications/{id}/
알림 상세 조회 (인증 필요).

응답 바디: 알림 목록 항목과 동일.

상태 코드: 200, 401, 404

### GET /api/notifications/unread/
읽지 않은 알림 목록 조회 (인증 필요).

응답 바디: 알림 목록 항목과 동일.

상태 코드: 200, 401

### PATCH /api/notifications/{id}/read/
알림 읽음 처리 (인증 필요).

응답 바디 (200): 알림 목록 항목과 동일.

상태 코드: 200, 401, 404
