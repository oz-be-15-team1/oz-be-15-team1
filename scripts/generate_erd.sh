#!/bin/sh
set -e

OUT_DIR=${1:-docs}
OUT_FILE=${2:-erd.png}
DOT_FILE="${OUT_FILE%.png}.dot"

mkdir -p "$OUT_DIR"
uv run python manage.py graph_models -a -g --dot > "$OUT_DIR/$DOT_FILE"
dot -Tpng "$OUT_DIR/$DOT_FILE" -o "$OUT_DIR/$OUT_FILE"
