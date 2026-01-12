# Budget API 스펙 (표 형식)

아래 표는 노션/구글 시트에 그대로 복사해 사용할 수 있는 요약 스펙입니다.

| 구분 | 엔드포인트 | 메서드 | 설명 | 인증 | 요청 바디 | 응답 바디 | 상태 코드 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Users | /api/users/signup/ | POST | 회원가입 | 없음 | email, password, name, phone | id, email, name, phone | 201, 400, 409 |
| Users | /api/users/login/ | POST | 로그인 | 없음 | email, password | user, token | 200, 400, 401 |
| Users | /api/users/logout/ | POST | 로그아웃 | Bearer | refresh | detail | 200, 400, 401 |
| Users | /api/users/profile/ | GET | 내 프로필 조회 | Bearer | - | id, email, name, phone | 200, 401 |
| Users | /api/users/profile/ | PATCH | 내 프로필 수정 | Bearer | name, phone | id, email, name, phone | 200, 400, 401 |
| Users | /api/users/profile/ | DELETE | 내 계정 삭제 | Bearer | - | detail | 200, 401 |
| Accounts | /api/accounts/ | GET | 계좌 목록 조회 | Bearer | - | AccountResponse[] | 200, 401 |
| Accounts | /api/accounts/ | POST | 계좌 생성 | Bearer | AccountCreate | AccountResponse | 201, 400, 401 |
| Accounts | /api/accounts/{id}/ | GET | 계좌 상세 조회 | Bearer | - | AccountResponse | 200, 401, 404 |
| Accounts | /api/accounts/{id}/ | DELETE | 계좌 삭제 | Bearer | - | - | 204, 401, 404 |
| Transactions | /api/transactions/ | GET | 거래 목록 조회(필터) | Bearer | - | TransactionResponse[] | 200, 401 |
| Transactions | /api/transactions/ | POST | 거래 생성 | Bearer | TransactionCreate | TransactionResponse | 201, 400, 401 |
| Transactions | /api/transactions/{id}/ | GET | 거래 상세 조회 | Bearer | - | TransactionResponse | 200, 401, 404 |
| Transactions | /api/transactions/{id}/ | PATCH | 거래 수정 | Bearer | TransactionUpdate | TransactionResponse | 200, 400, 401, 404 |
| Transactions | /api/transactions/{id}/ | DELETE | 거래 삭제 | Bearer | - | - | 204, 401, 404 |
| Categories | /api/categories/ | GET | 카테고리 목록 조회 | Bearer | - | CategoryRead[] | 200, 401 |
| Categories | /api/categories/ | POST | 카테고리 생성 | Bearer | CategoryCreateUpdate | CategoryRead | 201, 400, 401 |
| Categories | /api/categories/{category_id}/ | GET | 카테고리 상세 조회 | Bearer | - | CategoryRead | 200, 401, 404 |
| Categories | /api/categories/{category_id}/ | PATCH | 카테고리 수정 | Bearer | CategoryCreateUpdate | CategoryRead | 200, 400, 401, 404 |
| Categories | /api/categories/{category_id}/ | DELETE | 카테고리 삭제(소프트) | Bearer | - | - | 204, 401, 404 |
| Categories | /api/categories/trash/ | GET | 삭제된 카테고리 목록 | Bearer | - | CategoryRead[] | 200, 401 |
| Categories | /api/categories/{category_id}/restore/ | POST | 카테고리 복구 | Bearer | - | - | 200, 401, 404 |
| Tags | /api/tags/ | GET | 태그 목록 조회 | Bearer | - | TagRead[] | 200, 401 |
| Tags | /api/tags/ | POST | 태그 생성 | Bearer | TagCreateUpdate | TagRead | 201, 400, 401 |
| Tags | /api/tags/{tag_id}/ | GET | 태그 상세 조회 | Bearer | - | TagRead | 200, 401, 404 |
| Tags | /api/tags/{tag_id}/ | PATCH | 태그 수정 | Bearer | TagCreateUpdate | TagRead | 200, 400, 401, 404 |
| Tags | /api/tags/{tag_id}/ | DELETE | 태그 삭제(소프트) | Bearer | - | - | 204, 401, 404 |
| Tags | /api/tags/trash/ | GET | 삭제된 태그 목록 | Bearer | - | TagRead[] | 200, 401 |
| Tags | /api/tags/{tag_id}/restore/ | POST | 태그 복구 | Bearer | - | - | 200, 401, 404 |
| Analysis | /api/analyses/ | GET | 분석 목록 조회 | Bearer | - | Analysis[] | 200, 401 |
| Analysis | /api/analyses/{id}/ | GET | 분석 상세 조회 | Bearer | - | Analysis | 200, 401, 404 |
| Analysis | /api/analyses/period/ | GET | 분석 필터 조회 | Bearer | - | Analysis[] | 200, 401 |
| Analysis | /api/analyses/run/ | POST | 분석 실행 요청 | Bearer | about, type, period_start, period_end | task_id | 202, 400, 401 |
| Analysis | /api/analyses/tasks/{task_id}/ | GET | 분석 작업 상태 | Bearer | - | status, result, date_done | 200, 401 |
| Notifications | /api/notifications/ | GET | 알림 목록 조회 | Bearer | - | Notification[] | 200, 401 |
| Notifications | /api/notifications/{id}/ | GET | 알림 상세 조회 | Bearer | - | Notification | 200, 401, 404 |
| Notifications | /api/notifications/unread/ | GET | 읽지 않은 알림 목록 | Bearer | - | Notification[] | 200, 401 |
| Notifications | /api/notifications/{id}/read/ | PATCH | 알림 읽음 처리 | Bearer | - | Notification | 200, 401, 404 |

요약 타입 정의:
- AccountCreate: name, source_type, balance, account_number, account_type, card_company, card_number, billing_day
- AccountResponse: id, name, source_type, balance, is_active, account_number, account_type, card_company, card_number, billing_day, created_at, updated_at
- TransactionCreate: account, amount, direction, method, description, occurred_at, tags
- TransactionUpdate: amount, direction, method, description, occurred_at, tags
- TransactionResponse: id, account, account_name, amount, balance_after, direction, method, description, tags, occurred_at, created_at, updated_at
- CategoryCreateUpdate: id, name, kind, sort_order, parent
- CategoryRead: id, name, kind, sort_order, parent, created_at
- TagCreateUpdate: id, name, color
- TagRead: id, name, color, created_at
- Analysis: id, user, about, type, period_start, period_end, description, result_image, created_at, updated_at
- Notification: id, user, message, is_read, created_at
