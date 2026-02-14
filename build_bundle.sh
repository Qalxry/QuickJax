#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDERER_DIR="$SCRIPT_DIR/renderer_src"
OUT_FILE="$SCRIPT_DIR/quickjax/js/mathjax_bundle.js"

echo "==> Installing npm dependencies..."
cd "$RENDERER_DIR"
npm install --silent

echo "==> Building MathJax bundle with esbuild..."
npx esbuild index.js \
  --bundle \
  --minify \
  --platform=browser \
  --format=iife \
  --outfile="$OUT_FILE"

SIZE=$(wc -c < "$OUT_FILE")
echo "==> Bundle created: $OUT_FILE ($SIZE bytes)"
