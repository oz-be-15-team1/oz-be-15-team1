.PHONY: help up down logs migrate run test lint fix fmt erd frontend precommit

help:
	# 사용 가능한 명령 목록 출력
	@echo "명령 목록:"
	@echo "  up         - 도커 컨테이너 실행 (개발)"
	@echo "  down       - 도커 컨테이너 중지"
	@echo "  logs       - 백엔드 로그 보기"
	@echo "  migrate    - 도커에서 마이그레이션 실행"
	@echo "  run        - 로컬 Django 개발 서버 실행"
	@echo "  test       - 로컬 테스트 실행"
	@echo "  lint       - ruff 린트 실행"
	@echo "  fix        - ruff 자동 수정"
	@echo "  fmt        - ruff 포맷 실행"
	@echo "  erd        - ERD 생성 (docs/erd.png)"
	@echo "  frontend   - 프론트 개발 서버 실행"
	@echo "  precommit  - pre-commit 훅 설치"

up:
	# 로컬 개발용 도커 컨테이너 실행
	docker compose -f docker-compose.dev.yml up -d --build

down:
	# 로컬 개발용 도커 컨테이너 중지
	docker compose -f docker-compose.dev.yml down

logs:
	# 백엔드 컨테이너 로그 확인
	docker compose -f docker-compose.dev.yml logs -f web

migrate:
	# 도커 환경에서 마이그레이션 실행
	docker compose -f docker-compose.dev.yml exec web uv run python manage.py migrate

run:
	# 로컬에서 Django 개발 서버 실행
	uv run python manage.py runserver

test:
	# 로컬 테스트 실행
	uv run python manage.py test

lint:
	# ruff 린트 실행
	uv run ruff check .

fix:
	# ruff 자동 수정
	uv run ruff check . --fix

fmt:
	# ruff 포맷 실행
	uv run ruff format

erd:
	# ERD 생성 (docs/erd.png)
	./scripts/generate_erd.sh

frontend:
	# 프론트엔드 개발 서버 실행
	cd frontend && npm install && npm run dev

precommit:
	# pre-commit 훅 설치
	uv run pre-commit install
