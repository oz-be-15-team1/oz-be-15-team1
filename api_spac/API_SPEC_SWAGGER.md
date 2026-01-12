# Budget API 스펙 (Swagger/DRF 스키마 기준)

이 문서는 `config/urls.py`와 각 app의 `urls.py`, `views.py`, `serializers.py` 기준으로 정리된 Swagger/DRF 스타일 스펙입니다.

## 공통

- Base URL: `/api`
- 인증: `Authorization: Bearer <token>`
- Content-Type: `application/json`
- Tags: 회원 관리, 계좌 관리, 거래 관리, 카테고리 관리, 태그 관리, 분석 관리, 알림 관리

## 회원 관리

### POST /api/users/signup/
- Summary: 회원가입
- Request Body: `RegisterSerializer`
- Response: `UserSignupResponseSerializer`
- Status: 201, 400

Request (example)
```json
{ "email": "user@example.com", "password": "securepassword123", "name": "홍길동", "phone": "010-1234-5678" }
```

Response (example)
```json
{ "id": 1, "email": "user@example.com", "name": "홍길동", "phone": "010-1234-5678" }
```

### POST /api/users/login/
- Summary: 로그인
- Request Body: `UserLoginRequestSerializer`
- Response: `UserLoginResponseSerializer`
- Status: 200, 401

Request (example)
```json
{ "email": "user@example.com", "password": "securepassword123" }
```

Response (example)
```json
{ "user": { "id": 1, "email": "user@example.com", "name": "홍길동", "phone": "010-1234-5678" }, "token": "jwt-access-token" }
```

### POST /api/users/logout/
- Summary: 로그아웃
- Auth: 필요
- Status: 200, 400

Request (example)
```json
{ "refresh": "jwt-refresh-token" }
```

Response (example)
```json
{ "detail": "Logout successful" }
```

### GET /api/users/profile/
- Summary: 프로필 조회
- Auth: 필요
- Response: `UserProfileSerializer`
- Status: 200, 401

### PATCH /api/users/profile/
- Summary: 프로필 수정
- Auth: 필요
- Request Body: `UserProfileSerializer` (partial)
- Response: `UserProfileSerializer`
- Status: 200, 400, 401

### DELETE /api/users/profile/
- Summary: 계정 삭제
- Auth: 필요
- Status: 200, 401

## 계좌 관리

### GET /api/accounts/
- Summary: 계좌 목록 조회
- Auth: 필요
- Response: `AccountResponseSerializer[]`
- Status: 200, 401

### POST /api/accounts/
- Summary: 계좌 생성
- Auth: 필요
- Request Body: `AccountCreateRequestSerializer`
- Response: `AccountResponseSerializer`
- Status: 201, 400, 401

### GET /api/accounts/{id}/
- Summary: 계좌 상세 조회
- Auth: 필요
- Response: `AccountResponseSerializer`
- Status: 200, 401, 404

### DELETE /api/accounts/{id}/
- Summary: 계좌 삭제
- Auth: 필요
- Status: 204, 401, 404

## 거래 관리

### GET /api/transactions/
- Summary: 거래 목록 조회
- Auth: 필요
- Query Params: account, direction, min_amount, max_amount, start_date, end_date
- Response: `TransactionResponseSerializer[]`
- Status: 200, 401

### POST /api/transactions/
- Summary: 거래 생성
- Auth: 필요
- Request Body: `TransactionCreateRequestSerializer`
- Response: `TransactionResponseSerializer`
- Status: 201, 400, 401

### GET /api/transactions/{id}/
- Summary: 거래 상세 조회
- Auth: 필요
- Response: `TransactionResponseSerializer`
- Status: 200, 401, 404

### PATCH /api/transactions/{id}/
- Summary: 거래 수정
- Auth: 필요
- Request Body: `TransactionUpdateRequestSerializer`
- Response: `TransactionResponseSerializer`
- Status: 200, 400, 401, 404

### DELETE /api/transactions/{id}/
- Summary: 거래 삭제
- Auth: 필요
- Status: 204, 401, 404

## 카테고리 관리

### GET /api/categories/
- Summary: 카테고리 목록 조회
- Auth: 필요
- Response: `CategoryReadSerializer[]`
- Status: 200, 401

### POST /api/categories/
- Summary: 카테고리 생성
- Auth: 필요
- Request Body: `CategoryCreateUpdateSerializer`
- Response: `CategoryReadSerializer`
- Status: 201, 400, 401

### GET /api/categories/{category_id}/
- Summary: 카테고리 상세 조회
- Auth: 필요
- Response: `CategoryReadSerializer`
- Status: 200, 401, 404

### PATCH /api/categories/{category_id}/
- Summary: 카테고리 수정
- Auth: 필요
- Request Body: `CategoryCreateUpdateSerializer`
- Response: `CategoryReadSerializer`
- Status: 200, 400, 401, 404

### DELETE /api/categories/{category_id}/
- Summary: 카테고리 삭제(소프트)
- Auth: 필요
- Status: 204, 401, 404

### GET /api/categories/trash/
- Summary: 삭제된 카테고리 목록
- Auth: 필요
- Response: `CategoryReadSerializer[]`
- Status: 200, 401

### POST /api/categories/{category_id}/restore/
- Summary: 카테고리 복구
- Auth: 필요
- Status: 200, 401, 404

## 태그 관리

### GET /api/tags/
- Summary: 태그 목록 조회
- Auth: 필요
- Response: `TagReadSerializer[]`
- Status: 200, 401

### POST /api/tags/
- Summary: 태그 생성
- Auth: 필요
- Request Body: `TagCreateUpdateSerializer`
- Response: `TagReadSerializer`
- Status: 201, 400, 401

### GET /api/tags/{tag_id}/
- Summary: 태그 상세 조회
- Auth: 필요
- Response: `TagReadSerializer`
- Status: 200, 401, 404

### PATCH /api/tags/{tag_id}/
- Summary: 태그 수정
- Auth: 필요
- Request Body: `TagCreateUpdateSerializer`
- Response: `TagReadSerializer`
- Status: 200, 400, 401, 404

### DELETE /api/tags/{tag_id}/
- Summary: 태그 삭제(소프트)
- Auth: 필요
- Status: 204, 401, 404

### GET /api/tags/trash/
- Summary: 삭제된 태그 목록
- Auth: 필요
- Response: `TagReadSerializer[]`
- Status: 200, 401

### POST /api/tags/{tag_id}/restore/
- Summary: 태그 복구
- Auth: 필요
- Status: 200, 401, 404

## 분석 관리

### GET /api/analyses/
- Summary: 분석 목록 조회
- Auth: 필요
- Response: `AnalysisSerializer[]`
- Status: 200, 401

### GET /api/analyses/{id}/
- Summary: 분석 상세 조회
- Auth: 필요
- Response: `AnalysisSerializer`
- Status: 200, 401, 404

### GET /api/analyses/period/
- Summary: 분석 목록 필터 조회
- Auth: 필요
- Query Params: type (weekly|monthly)
- Response: `AnalysisSerializer[]`
- Status: 200, 401

### POST /api/analyses/run/
- Summary: 분석 실행 요청
- Auth: 필요
- Request Body: about, type, period_start, period_end
- Response: task_id
- Status: 202, 400, 401

### GET /api/analyses/tasks/{task_id}/
- Summary: 분석 작업 상태
- Auth: 필요
- Response: status, result, date_done
- Status: 200, 401

## 알림 관리

### GET /api/notifications/
- Summary: 알림 목록 조회
- Auth: 필요
- Response: `NotificationSerializer[]`
- Status: 200, 401

### GET /api/notifications/{id}/
- Summary: 알림 상세 조회
- Auth: 필요
- Response: `NotificationSerializer`
- Status: 200, 401, 404

### GET /api/notifications/unread/
- Summary: 읽지 않은 알림 목록
- Auth: 필요
- Response: `NotificationSerializer[]`
- Status: 200, 401

### PATCH /api/notifications/{id}/read/
- Summary: 알림 읽음 처리
- Auth: 필요
- Response: `NotificationSerializer`
- Status: 200, 401, 404

## Serializer 필드 요약

### RegisterSerializer
- email (EmailField)
- password (write_only)
- name (CharField)
- phone (CharField)

### UserSignupResponseSerializer
- id, email, name, phone

### UserLoginRequestSerializer
- email, password

### UserLoginResponseSerializer
- user (UserSignupResponseSerializer), token

### UserProfileSerializer
- id, email, name, phone (email read_only)

### AccountCreateRequestSerializer
- name, source_type, balance, account_number, account_type, card_company, card_number, billing_day

### AccountResponseSerializer
- id, name, source_type, balance, is_active, account_number, account_type, card_company, card_number, billing_day, created_at, updated_at

### TransactionCreateRequestSerializer
- account, amount, direction, method, description, occurred_at, tags

### TransactionUpdateRequestSerializer
- amount, direction, method, description, occurred_at, tags

### TransactionResponseSerializer
- id, account, account_name, amount, balance_after, direction, method, description, tags, occurred_at, created_at, updated_at

### CategoryCreateUpdateSerializer
- id, name, kind, sort_order, parent

### CategoryReadSerializer
- id, name, kind, sort_order, parent, created_at

### TagCreateUpdateSerializer
- id, name, color

### TagReadSerializer
- id, name, color, created_at

### AnalysisSerializer
- fields = "__all__"

### NotificationSerializer
- fields = "__all__"
