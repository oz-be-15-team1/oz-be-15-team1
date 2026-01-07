from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    name = "apps.analysis"

    def ready(self):
        from . import signals  # noqa: F401
