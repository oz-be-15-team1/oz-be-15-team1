import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("budget")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "weekly-expense-analysis": {
        "task": "apps.analysis.tasks.run_weekly_expense_analysis",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),
    },
    "monthly-income-analysis": {
        "task": "apps.analysis.tasks.run_monthly_income_analysis",
        "schedule": crontab(day_of_month=1, hour=10, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
