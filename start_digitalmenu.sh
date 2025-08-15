#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="/home/ubuntu/evoo_digitalmenu/test_evolusys/digitalmenu/python"
LOG_DIR="/var/log"
BACKEND_LOG="$LOG_DIR/digitalmenu_backend.log"

touch "$BACKEND_LOG"
chmod 664 "$BACKEND_LOG"

fuser -k 8095/tcp 2>/dev/null || true

cd "$BACKEND_DIR"
/usr/bin/python3 run.py >> "$BACKEND_LOG" 2>&1
