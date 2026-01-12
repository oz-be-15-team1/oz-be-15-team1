from django.db import models

from apps.common.models import SoftDeleteManager
from apps.members.models import User
from apps.trashcan.models import TrashableModel


class Analysis(TrashableModel):
    """
    사용자 분석 결과 모델.
    """

    ANALYSIS_TYPE_CHOICES = [
        ("weekly", "매주"),
        ("monthly", "매월"),
    ]

    ANALYSIS_ABOUT_CHOICES = [
        ("total_expense", "총 지출"),
        ("total_income", "총 수입"),
        ("category_expense", "카테고리별 지출"),
        ("account_balance", "계좌 잔액"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses")
    about = models.CharField(max_length=100, choices=ANALYSIS_ABOUT_CHOICES)
    type = models.CharField(max_length=50, choices=ANALYSIS_TYPE_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    description = models.TextField()
    result_image = models.ImageField(upload_to="analysis_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #  soft delete 기본 매니저
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.user.email} - {self.about} ({self.type})"
