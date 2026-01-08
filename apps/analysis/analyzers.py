import os
from datetime import datetime
from decimal import Decimal

import matplotlib
import pandas as pd
from django.conf import settings

from apps.transaction.models import Transaction

from .models import Analysis

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class Analyzer:
    def __init__(self, user):
        self.user = user

    def get_transactions_in_period(self, start_date, end_date):
        return (
            Transaction.objects.filter(
                account__user=self.user,
                occurred_at__date__gte=start_date,
                occurred_at__date__lte=end_date,
            )
            .select_related("account")
            .order_by("occurred_at")
        )

    def create_dataframe(self, transactions):
        data = [
            {
                "date": transaction.occurred_at.date(),
                "amount": transaction.amount,
                "direction": transaction.direction,
                "method": transaction.method,
                "description": transaction.description,
                "account_name": transaction.account.name,
                "balance_after": transaction.balance_after,
            }
            for transaction in transactions
        ]
        return pd.DataFrame(data)

    def analyze_total_expense(self, df, start_date, end_date):
        expense_df = df[df["direction"] == "expense"]
        daily_expense = expense_df.groupby("date")["amount"].sum().reset_index()

        plt.figure(figsize=(10, 6))
        plt.plot(daily_expense["date"], daily_expense["amount"], marker="o")
        plt.title(f"총 지출 분석 ({start_date} ~ {end_date})")
        plt.xlabel("날짜")
        plt.ylabel("지출 금액")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        return plt, f"총 지출: {self.format_currency(expense_df['amount'].sum())}"

    def analyze_total_income(self, df, start_date, end_date):
        income_df = df[df["direction"] == "income"]
        daily_income = income_df.groupby("date")["amount"].sum().reset_index()

        plt.figure(figsize=(10, 6))
        plt.bar(daily_income["date"].astype(str), daily_income["amount"], color="green", alpha=0.7)
        plt.title(f"총 수입 분석 ({start_date} ~ {end_date})")
        plt.xlabel("날짜")
        plt.ylabel("수입 금액")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis="y")

        return plt, f"총 수입: {self.format_currency(income_df['amount'].sum())}"

    def analyze_category_expense(self, df, start_date, end_date):
        expense_df = df[df["direction"] == "expense"]
        category_expense = expense_df.groupby("method")["amount"].sum().reset_index()

        plt.figure(figsize=(10, 6))
        plt.pie(category_expense["amount"], labels=category_expense["method"], autopct="%1.1f%%")
        plt.title(f"카테고리별 지출 분석 ({start_date} ~ {end_date})")

        if category_expense.empty:
            return plt, "카테고리별 지출 없음"

        breakdown = ", ".join(
            f"{row['method']}: {self.format_currency(row['amount'])}"
            for _, row in category_expense.iterrows()
        )
        return plt, f"카테고리별 지출 - {breakdown}"

    def analyze_account_balance(self, df, start_date, end_date):
        latest_balances = (
            df.sort_values("date").groupby("account_name").last()["balance_after"].reset_index()
        )

        plt.figure(figsize=(10, 6))
        plt.bar(
            latest_balances["account_name"],
            latest_balances["balance_after"],
            color="blue",
            alpha=0.7,
        )
        plt.title(f"계좌별 잔액 분석 ({end_date} 기준)")
        plt.xlabel("계좌명")
        plt.ylabel("잔액")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis="y")

        return plt, f"총 잔액: {self.format_currency(latest_balances['balance_after'].sum())}"

    def save_plot_image(self, plot, filename):
        image_path = os.path.join(settings.MEDIA_ROOT, "analysis_images", filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        plot.savefig(image_path, bbox_inches="tight", dpi=150)
        plot.close()
        return f"analysis_images/{filename}"

    def run_analysis(self, analysis_type, period_type, start_date, end_date):
        transactions = self.get_transactions_in_period(start_date, end_date)
        if not transactions.exists():
            raise ValueError("분석할 거래 내역이 없습니다.")

        df = self.create_dataframe(transactions)

        analysis_methods = {
            "total_expense": self.analyze_total_expense,
            "total_income": self.analyze_total_income,
            "category_expense": self.analyze_category_expense,
            "account_balance": self.analyze_account_balance,
        }

        if analysis_type not in analysis_methods:
            raise ValueError(f"지원하지 않는 분석 유형: {analysis_type}")

        plot, description = analysis_methods[analysis_type](df, start_date, end_date)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{analysis_type}_{period_type}_{timestamp}.png"
        image_path = self.save_plot_image(plot, filename)

        return Analysis.objects.create(
            user=self.user,
            about=analysis_type,
            type=period_type,
            period_start=start_date,
            period_end=end_date,
            description=description,
            result_image=image_path,
        )

    @staticmethod
    def format_currency(value):
        if isinstance(value, Decimal):
            value = int(value.quantize(Decimal("1")))
        else:
            value = int(round(value))
        return f"{value:,}원"
