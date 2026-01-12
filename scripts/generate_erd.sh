#!/bin/sh
set -e

OUT_DIR=${1:-docs}
OUT_FILE=${2:-erd.png}

mkdir -p "$OUT_DIR"
uv run python manage.py graph_models -a -g -o "$OUT_DIR/$OUT_FILE"
