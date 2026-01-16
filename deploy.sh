#!/usr/bin/env bash
set -euo pipefail

cd /home/ubuntu/oz-be-15-team1

echo "[1/6] git pull"
git pull origin main

echo "[2/6] install deps (uv)"
UV="$HOME/.local/bin/uv"
if [ ! -x "$UV" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
"$UV" sync --frozen

echo "[3/6] deploy"
# TODO: 여기에 실제 배포 명령을 넣어야 함 (docker/systemd/django 등)
# 예시:
# "$UV" run python manage.py migrate
# "$UV" run python manage.py collectstatic --noinput
# sudo systemctl restart gunicorn

echo "deploy.sh finished"
