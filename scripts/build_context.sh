#!/usr/bin/env bash
set -euo pipefail

OUTPUT_FILE="${OUTPUT_FILE:-context/repomix-output.xml}"

rm -f "$OUTPUT_FILE"
npx repomix@latest --output "$OUTPUT_FILE"

echo
echo "Contexto generado:"
ls -lh "$OUTPUT_FILE"