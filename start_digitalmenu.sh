#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="/home/ubuntu/evoo_digitalmenu/test_evolusys/digitalmenu/python"
FRONTEND_DIR="/home/ubuntu/evoo_digitalmenu/test_evolusys/digitalmenu/angular"
LOG_DIR="/var/log"
BACKEND_LOG="$LOG_DIR/digitalmenu_backend.log"
FRONTEND_LOG="$LOG_DIR/digitalmenu_frontend.log"

# Ensure logs exist
touch "$BACKEND_LOG" "$FRONTEND_LOG"
chmod 664 "$BACKEND_LOG" "$FRONTEND_LOG"

# Extra safety: kill anything left behind on our ports
fuser -k 8095/tcp 2>/dev/null || true
fuser -k 4201/tcp 2>/dev/null || true

# Start backend (FastAPI/Uvicorn) on 8095
cd "$BACKEND_DIR"
/usr/bin/python3 run.py >> "$BACKEND_LOG" 2>&1 &
BACK_PID=$!

# Start frontend (Angular dev server) on 4201, public host
cd "$FRONTEND_DIR"
/usr/bin/npx --yes @angular/cli@19.2.8 serve --host 0.0.0.0 --port 4201 >> "$FRONTEND_LOG" 2>&1 &
FRONT_PID=$!

# Trap and propagate stop signals to both
trap "kill $BACK_PID $FRONT_PID 2>/dev/null || true" INT TERM

# Wait on both
wait $BACK_PID
wait $FRONT_PID
