#!/usr/bin/env bash
set -euo pipefail

: "${HF_TOKEN?Set HF_TOKEN env var or source .env}"

REPO="${1:?e.g. QuantFactory/CodeLlama-7B-GGUF}"
FILE="${2:?e.g. codellama-7b.Q4_K_M.gguf}"
OUT_DIR="${3:-data/models}"

mkdir -p "$OUT_DIR"
URL="https://huggingface.co/${REPO}/resolve/main/${FILE}"
OUT="${OUT_DIR}/${FILE}"

# Prefer aria2c if present, else curl
if command -v aria2c >/dev/null 2>&1; then
  aria2c -c -x 4 -s 4 --max-tries=0 --retry-wait=20 --file-allocation=none \
    --header="Authorization: Bearer ${HF_TOKEN}" \
    -o "${OUT}" "${URL}"
else
  curl -L -C - --retry 999 --retry-delay 20 \
    -H "Authorization: Bearer ${HF_TOKEN}" \
    -o "${OUT}" "${URL}"
fi

echo "Saved -> ${OUT}"
