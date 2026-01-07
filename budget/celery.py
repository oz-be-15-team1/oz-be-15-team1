import os

from celery import Celery
from celery.schedules import crontab

# Django 설정 모듈 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("budget")

# Django 설정에서 Celery 설정 로드
app.config_from_object("django.conf:settings", namespace="CELERY")

# 자동으로 tasks.py 파일에서 task 등록
app.autodiscover_tasks()

# 스케줄링 작업 설정
app.conf.beat_schedule = {
    "weekly-expense-analysis": {
        "task": "apps.analysis.tasks.run_weekly_expense_analysis",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),  # 매주 월요일 오전 9시
    },
    "monthly-income-analysis": {
        "task": "apps.analysis.tasks.run_monthly_income_analysis",
        "schedule": crontab(day_of_month=1, hour=10, minute=0),  # 매월 1일 오전 10시
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
