from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    """
    Analysis 앱 설정.
    """

    name = "apps.analysis"

    def ready(self):
        from . import signals  # noqa: F401
