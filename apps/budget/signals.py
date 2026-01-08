from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

from .services import trigger_budget_alerts_for_transaction


def _get_transaction_model():
    return apps.get_model("transaction", "Transaction")


Transaction = _get_transaction_model()


@receiver(post_save, sender=Transaction)
def on_transaction_saved(sender, instance, created, **kwargs):
    # created(새로 생성)일 때만 처리하고 싶으면 아래처럼:
    if not created:
        return

    trigger_budget_alerts_for_transaction(instance)
