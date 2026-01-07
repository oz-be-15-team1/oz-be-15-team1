from .base import *  # noqa
import sys

DEBUG = True
ALLOWED_HOSTS = ["*"]

# django-debug-toolbar 설정 (테스트 실행 시 비활성화)
TESTING = "test" in sys.argv

if not TESTING:
    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE  # noqa: F405

# django-debug-toolbar를 표시할 IP 주소 설정
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Docker 환경에서 django-debug-toolbar 사용 설정
import socket  # noqa: E402

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [ip[: ip.rfind(".")] + ".1" for ip in ips]

# django-debug-toolbar 패널 설정
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,  # noqa: F405
}
