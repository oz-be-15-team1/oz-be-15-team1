from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.members.models import User

from .analyzers import Analyzer


@shared_task
def run_weekly_expense_analysis():
    """매주 월요일에 모든 사용자의 주간 지출 분석 실행"""
    users = User.objects.all()
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)

    for user in users:
        try:
            analyzer = Analyzer(user)
            analyzer.run_analysis("total_expense", "weekly", start_date, end_date)
        except Exception as e:
            print(f"Error analyzing user {user.email}: {e}")


@shared_task
def run_monthly_income_analysis():
    """매월 1일에 모든 사용자의 월간 수입 분석 실행"""
    users = User.objects.all()
    # 전월 분석
    today = timezone.now().date()
    end_date = today.replace(day=1) - timedelta(days=1)  # 전월 말일
    start_date = end_date.replace(day=1)  # 전월 1일

    for user in users:
        try:
            analyzer = Analyzer(user)
            analyzer.run_analysis("total_income", "monthly", start_date, end_date)
        except Exception as e:
            print(f"Error analyzing user {user.email}: {e}")


@shared_task
def run_user_analysis(user_id, analysis_type, period_type, start_date, end_date):
    """특정 사용자의 분석 실행"""
    try:
        user = User.objects.get(id=user_id)
        analyzer = Analyzer(user)
        analysis = analyzer.run_analysis(analysis_type, period_type, start_date, end_date)
        return f"Analysis completed for user {user.email}: {analysis.id}"
    except User.DoesNotExist:
        return f"User {user_id} not found"
    except Exception as e:
        return f"Error: {e}"
