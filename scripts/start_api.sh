#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_DIR="${LOG_DIR:-outputs/logs}"
PID_FILE="${PID_FILE:-outputs/api.pid}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

mkdir -p "$LOG_DIR"
mkdir -p "$(dirname "$PID_FILE")"

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"

  if kill -0 "$PID" 2>/dev/null && ps -p "$PID" -o args= | grep -q "uvicorn src.main:app"; then
    echo "La API ya está corriendo con PID $PID"
    exit 0
  fi

  echo "PID file obsoleto. Limpiando $PID_FILE."
  rm -f "$PID_FILE"
fi

echo "Levantando API en http://$HOST:$PORT ..."

nohup uv run uvicorn src.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --log-level info \
  > "$LOG_DIR/api.log" 2>&1 &

echo $! > "$PID_FILE"

echo "API iniciada con PID $(cat "$PID_FILE")"
echo "Logs: $LOG_DIR/api.log"
echo
echo "Prueba:"
echo "  curl http://localhost:$PORT/health"