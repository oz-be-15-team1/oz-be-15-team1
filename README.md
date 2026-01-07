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

## Celery 스케줄링 작업 결과물

### Mission 1: Celery 설치 및 설정
- ✅ `celery`, `django-celery-beat`, `django-celery-results`, `redis` 패키지 설치
- ✅ INSTALLED_APPS에 celery 관련 앱 추가
- ✅ settings.py에 Celery 브로커 및 백엔드 설정
- ✅ `budget/celery.py` 생성 및 Celery 앱 구성
- ✅ `budget/__init__.py`에 celery_app import 추가

### Mission 2: 분석 Task 생성 및 스케줄링
- ✅ `apps/analysis/tasks.py` 생성
- ✅ `shared_task` 데코레이터 사용 (앱 간 공유 가능)
- ✅ 주간 지출 분석, 월간 수입 분석 Task 구현
- ✅ `celery.py`에 beat_schedule 설정으로 스케줄링 등록

### Mission 3: Celery 백그라운드 실행 확인
Celery 워커 및 beat 실행 결과:

```bash
# Redis 켜기 (필요시)
docker start local-redis

# 터미널 1: Celery 워커 실행
celery -A budget worker --loglevel=info
# uv 이용시
uv run celery -A budget worker --loglevel=info

# 터미널 2: Celery beat 실행
celery -A budget beat --loglevel=info
# uv 이용시
uv run celery -A budget beat --loglevel=info
```

실행 결과 스크린샷:
- 워커 실행: 작업 대기 중 상태 확인
- beat 실행: 스케줄링 작업 등록 확인
- Django admin에서 Periodic Tasks 및 Task Results 확인 가능

스케줄링 작업:
- 매주 월요일 09:00: 주간 지출 분석
- 매월 1일 10:00: 월간 수입 분석
