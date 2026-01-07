from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.members.models import User

from .analyzers import Analyzer


@shared_task
def run_weekly_expense_analysis():
    users = User.objects.all()
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)

    for user in users:
        try:
            analyzer = Analyzer(user)
            analyzer.run_analysis("total_expense", "weekly", start_date, end_date)
        except Exception as exc:
            print(f"Error analyzing user {user.email}: {exc}")


@shared_task
def run_monthly_income_analysis():
    users = User.objects.all()
    today = timezone.now().date()
    end_date = today.replace(day=1) - timedelta(days=1)
    start_date = end_date.replace(day=1)

    for user in users:
        try:
            analyzer = Analyzer(user)
            analyzer.run_analysis("total_income", "monthly", start_date, end_date)
        except Exception as exc:
            print(f"Error analyzing user {user.email}: {exc}")


@shared_task
def run_user_analysis(user_id, analysis_type, period_type, start_date, end_date):
    try:
        user = User.objects.get(id=user_id)
        analyzer = Analyzer(user)
        analysis = analyzer.run_analysis(analysis_type, period_type, start_date, end_date)
        return f"Analysis completed for user {user.email}: {analysis.id}"
    except User.DoesNotExist:
        return f"User {user_id} not found"
    except Exception as exc:
        return f"Error: {exc}"
