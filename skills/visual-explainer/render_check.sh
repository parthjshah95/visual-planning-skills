#!/usr/bin/env bash
# render_check.sh — render an HTML deck in headless Chrome, print its layout-audit
# lines, and write one screenshot per scene for you to look at.
#
# Usage: render_check.sh <file.html> [--out DIR] [--size WxH] [--scenes N]
# Needs: the page inlines layout_audit.js; Chrome or Chromium on this machine.
# Exit 0 when the audit reports zero warnings, 2 when it reports any, 1 on error.
set -euo pipefail
FILE="${1:-}"; [ -f "$FILE" ] || { echo "usage: $0 <file.html> [--out DIR] [--size WxH] [--scenes N]" >&2; exit 1; }
shift
OUT="$(dirname "$FILE")/render-check"; SIZE="1400,1000"; SCENES=""
while [ $# -gt 0 ]; do
    case "$1" in
        --out) OUT="$2"; shift 2 ;;
        --size) SIZE="${2/x/,}"; shift 2 ;;
        --scenes) SCENES="$2"; shift 2 ;;
        *) echo "unknown flag: $1" >&2; exit 1 ;;
    esac
done

CHROME="${CHROME:-}"
for candidate in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" google-chrome chromium chromium-browser chrome; do
    [ -n "$CHROME" ] && break
    if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then CHROME="$candidate"; fi
done
[ -n "$CHROME" ] || { echo "no Chrome/Chromium found; set CHROME=/path/to/chrome" >&2; exit 1; }

URL="file://$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
FLAGS=(--headless=new --disable-gpu --no-sandbox --hide-scrollbars --virtual-time-budget=5000 "--window-size=$SIZE")
mkdir -p "$OUT"
STEM="$(basename "${FILE%.*}")"

audit="$("$CHROME" "${FLAGS[@]}" --dump-dom "$URL" 2>/dev/null | sed -n '/<pre id="layout-audit"/,/<\/pre>/p' | grep -o 'layout-audit: [^<]*' || true)"
[ -n "$audit" ] || { echo "no layout-audit output: is layout_audit.js inlined at the end of <body>?" >&2; exit 1; }
printf '%s\n' "$audit"

[ -n "$SCENES" ] || SCENES="$(printf '%s\n' "$audit" | sed -n 's/.*done (\([0-9]*\) state.*/\1/p')"
for n in $(seq 1 "${SCENES:-1}"); do
    "$CHROME" "${FLAGS[@]}" "--screenshot=$OUT/$STEM.scene-$n.png" "$URL#scene=$n" >/dev/null 2>&1
    echo "screenshot: $OUT/$STEM.scene-$n.png"
done

if printf '%s\n' "$audit" | grep -q 'done (.*, 0 warnings)'; then exit 0; else exit 2; fi
