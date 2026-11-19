#!/usr/bin/env bash
# Render each fig*.svg here (or in the folder given as $1) to a true-size PDF (170 mm wide = A4 text width, vector)
# and a ~350 dpi PNG, using headless Chrome.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
WIDTH_MM=170
cd "$HERE/${1:-.}"; HERE="$(pwd)"   # optional arg: a subfolder, e.g. drafts
for svg in fig*.svg; do
  base="${svg%.svg}"
  dims=$(grep -o 'width="[0-9]*" height="[0-9]*"' "$svg" | head -1 | grep -o '[0-9]*')
  W=$(echo "$dims" | sed -n 1p); H=$(echo "$dims" | sed -n 2p)
  HMM=$(awk "BEGIN{printf \"%.2f\", $WIDTH_MM*$H/$W}")
  cat > "_$base.html" <<HTML
<!doctype html><meta charset="utf-8"><style>@page{size:${WIDTH_MM}mm ${HMM}mm;margin:0}
html,body{margin:0;padding:0;background:#fff}img{display:block;width:100%;height:auto}</style>
<img src="$svg">
HTML
  url="file:///$(cygpath -m "$HERE/_$base.html")"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2.5 \
    --window-size="$W,$H" --screenshot="$(cygpath -w "$HERE/$base.png")" "$url" 2>/dev/null
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$(cygpath -w "$HERE/$base.pdf")" "$url" 2>/dev/null
  rm -f "_$base.html"
  echo "rendered $base: ${WIDTH_MM} x ${HMM} mm"
done
