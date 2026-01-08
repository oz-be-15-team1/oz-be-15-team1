import os
from decimal import Decimal

import django


def format_currency(value):
    if isinstance(value, Decimal):
        value = int(value.quantize(Decimal("1")))
    else:
        value = int(round(value))
    return f"{value:,}원"


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    django.setup()
    from apps.analysis.models import Analysis
    from apps.transaction.models import Transaction

    analyses = Analysis.objects.filter(about="category_expense")
    updated = 0

    for analysis in analyses:
        tx_qs = Transaction.objects.filter(
            account__user=analysis.user,
            direction="expense",
            occurred_at__date__gte=analysis.period_start,
            occurred_at__date__lte=analysis.period_end,
        )
        if not tx_qs.exists():
            analysis.description = "카테고리별 지출 없음"
            analysis.save(update_fields=["description"])
            updated += 1
            continue

        summary = {}
        for tx in tx_qs:
            summary[tx.method] = summary.get(tx.method, Decimal("0")) + Decimal(tx.amount)

        breakdown = ", ".join(
            f"{method}: {format_currency(amount)}" for method, amount in summary.items()
        )
        analysis.description = f"카테고리별 지출 - {breakdown}"
        analysis.save(update_fields=["description"])
        updated += 1

    print(f"updated: {updated}")


if __name__ == "__main__":
    main()
