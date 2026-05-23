#!/usr/bin/env bash
set -euo pipefail

PID_FILE="${PID_FILE:-outputs/api.pid}"
PATTERN="${PATTERN:-uvicorn src.main:app}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"

  if kill -0 "$PID" 2>/dev/null && ps -p "$PID" -o args= | grep -q "$PATTERN"; then
    echo "Deteniendo API con PID $PID..."

    kill "$PID"

    for _ in {1..10}; do
      if ! kill -0 "$PID" 2>/dev/null; then
        break
      fi
      sleep 0.5
    done

    if kill -0 "$PID" 2>/dev/null; then
      echo "El proceso no terminó. Forzando kill -9..."
      kill -9 "$PID"
    fi

    rm -f "$PID_FILE"
    echo "API detenida."
    exit 0
  fi

  echo "PID file obsoleto. Limpiando $PID_FILE."
  rm -f "$PID_FILE"
fi

echo "No existe $PID_FILE. Intentando detener uvicorn por patrón..."

PIDS="$(pgrep -f "$PATTERN" || true)"

if [[ -z "$PIDS" ]]; then
  echo "La API no está corriendo."
  exit 0
fi

echo "Procesos encontrados:"
echo "$PIDS"

echo "Deteniendo procesos..."
echo "$PIDS" | xargs -r kill

sleep 1

STILL_RUNNING="$(pgrep -f "$PATTERN" || true)"

if [[ -n "$STILL_RUNNING" ]]; then
  echo "Algunos procesos siguen activos. Forzando kill -9..."
  echo "$STILL_RUNNING" | xargs -r kill -9
fi

rm -f "$PID_FILE"

echo "API detenida."
