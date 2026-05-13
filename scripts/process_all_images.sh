#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
IMGS_DIR="${IMGS_DIR:-imgs}"
OUTPUT_DIR="${OUTPUT_DIR:-output}"
CONCURRENCY="${CONCURRENCY:-3}"

PROMPT="${PROMPT:-Describe la imagen en español de forma clara y breve. Incluye también una lista corta de los elementos u objetos visibles.}"

mkdir -p "$OUTPUT_DIR/descriptions"

echo "API:         $API_URL"
echo "Imágenes:    $IMGS_DIR"
echo "Output:      $OUTPUT_DIR/descriptions"
echo "Concurrencia: $CONCURRENCY"
echo

# Validar que la API esté viva
curl -fsS "$API_URL/health" >/dev/null

echo "API OK"
echo

process_image() {
  local img_path="$1"
  local filename
  local stem
  local output_file

  filename="$(basename "$img_path")"
  stem="${filename%.*}"
  output_file="$OUTPUT_DIR/descriptions/${stem}.json"

  echo "Procesando: $filename"

  curl -fsS -X POST \
    -F "file=@${img_path}" \
    -F "prompt=${PROMPT}" \
    "$API_URL/describe-image" \
    -o "$output_file"

  echo "OK: $filename → $output_file"
}

export -f process_image
export API_URL OUTPUT_DIR PROMPT

find "$IMGS_DIR" -maxdepth 1 -type f \( \
  -iname "*.jpg" -o \
  -iname "*.jpeg" -o \
  -iname "*.png" -o \
  -iname "*.webp" \
\) -print0 \
  | xargs -0 -n 1 -P "$CONCURRENCY" bash -c 'process_image "$0"'

echo
echo "Proceso terminado."
echo "Resultados guardados en: $OUTPUT_DIR/descriptions"