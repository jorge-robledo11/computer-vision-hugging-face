#!/usr/bin/env bash
set -euo pipefail

MODEL_ID="unsloth/gemma-4-E4B-it-GGUF"
QUANT="Q5_K_M"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$(cd "$SCRIPT_DIR/../models" && pwd)"
MODEL_DIR="$TARGET_DIR/gemma-4-E4B-it"

mkdir -p "$MODEL_DIR"

echo "Repo:    $MODEL_ID"
echo "Destino: $MODEL_DIR"
echo "Quant:   $QUANT"
echo

echo "Descargando modelo GGUF $QUANT + mmproj..."

hf download "$MODEL_ID" \
  --include "*${QUANT}*.gguf" \
  --include "*mmproj*.gguf" \
  --local-dir "$MODEL_DIR"

echo
echo "Descarga completada:"
ls -lh "$MODEL_DIR"

echo
echo "Validando archivos..."

MODEL_FILE="$(find "$MODEL_DIR" -maxdepth 1 -type f -name "*${QUANT}*.gguf" ! -iname "*mmproj*" | head -n 1)"
MMPROJ_FILE="$(find "$MODEL_DIR" -maxdepth 1 -type f -iname "*mmproj*.gguf" | head -n 1)"

if [[ -z "${MODEL_FILE:-}" ]]; then
  echo "ERROR: No se encontró ningún modelo *${QUANT}*.gguf en $MODEL_DIR"
  exit 1
fi

if [[ -z "${MMPROJ_FILE:-}" ]]; then
  echo "ERROR: No se encontró ningún archivo *mmproj*.gguf en $MODEL_DIR"
  exit 1
fi

MODEL_SIZE_BYTES="$(stat -c%s "$MODEL_FILE")"
MODEL_SIZE_GB="$(numfmt --to=iec --suffix=B "$MODEL_SIZE_BYTES")"

echo "Modelo: $MODEL_FILE"
echo "Tamaño: $MODEL_SIZE_GB"
echo "MMProj: $MMPROJ_FILE"
echo
echo "OK: modelo multimodal listo para llama.cpp / llama-cpp-python."