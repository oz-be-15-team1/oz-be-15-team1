import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Wait for database to be available"

    def handle(self, *args, **options):
        db_conn = connections["default"]
        for attempt in range(1, 11):
            try:
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS("데이터베이스 연결 성공!"))
                return
            except OperationalError:
                self.stdout.write(f"데이터베이스 연결 실패, 1초 대기 중... ({attempt}/10)")
                time.sleep(1)
        self.stdout.write(self.style.ERROR("10번 시도 후 데이터베이스 연결 실패."))
