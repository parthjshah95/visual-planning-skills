#!/usr/bin/env bash
# Self-check for layout_audit.js + render_check.sh: a fixture page with one known
# defect of each kind, plus a clean box, rendered in headless Chrome.
# Run: bash skills/visual-explainer/test_layout_audit.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
{
cat <<'HTML'
<!doctype html><meta charset="utf-8"><title>fixture</title>
<style>
  .box{position:absolute;border:1px solid #333;width:100px;height:40px;white-space:nowrap}
  .stage[data-scene="2"] .late{display:block}
  .late{display:none}
</style>
<body>
<div class="box" id="clean" style="left:10px;top:10px">short</div>
<div class="box" id="spill" style="left:10px;top:80px">this text is far too long for a hundred pixel box</div>
<div class="box" id="a" style="left:10px;top:200px"></div>
<div class="box" id="b" style="left:60px;top:220px"></div>
<div class="stage" data-scene="1" data-scenes="2" style="position:absolute;left:400px;top:10px;width:300px;height:300px">
  <div class="box" id="s-one" style="left:0;top:0"></div>
  <div class="box late" id="s-two" style="left:50px;top:20px"></div>
  <svg width="300" height="100" style="position:absolute;top:150px">
    <g><rect x="10" y="10" width="60" height="30"/><text x="40" y="30" text-anchor="middle">this SVG label overruns its rectangle</text></g>
    <g><rect x="100" y="10" width="120" height="30"/><text x="110" y="30">fits</text></g>
  </svg>
</div>
<script>
HTML
cat "$HERE/layout_audit.js"
echo "</script></body>"
} > "$TMP/fixture.html"

out="$(bash "$HERE/render_check.sh" "$TMP/fixture.html" --out "$TMP/shots" 2>&1)" && code=0 || code=$?
pass=0; fail=0
check() { if printf '%s\n' "$out" | grep -q -- "$1"; then echo "ok   $2"; pass=$((pass+1)); else echo "FAIL $2"; fail=$((fail+1)); fi; }
nocheck() { if printf '%s\n' "$out" | grep -q -- "$1"; then echo "FAIL $2"; fail=$((fail+1)); else echo "ok   $2"; pass=$((pass+1)); fi; }

check   'scene 1: text spills out of div#spill'          "HTML text overflow is reported"
nocheck 'div#clean'                                       "clean box is not reported"
check   'scene 1: div#a overlaps div#b'                   "overlap between HTML boxes is reported"
check   'scene 2: div#s-one overlaps div#s-two'           "overlap that only exists in scene 2 is reported"
nocheck 'scene 1: div#s-one overlaps'                     "hidden scene-2 actor is not reported in scene 1"
check   'SVG text spills out of its shape: text "this SVG' "SVG text overflow is reported"
nocheck 'text "fits"'                                     "SVG text that fits is not reported"
check   'done (2 states'                                  "both scenes were audited"
check   'screenshot: .*fixture.scene-2.png'               "one screenshot per scene"
[ "$code" = 2 ] && { echo "ok   exit code 2 with warnings"; pass=$((pass+1)); } || { echo "FAIL exit code was $code, want 2"; fail=$((fail+1)); }
[ -s "$TMP/shots/fixture.scene-2.png" ] && { echo "ok   screenshot file exists"; pass=$((pass+1)); } || { echo "FAIL screenshot missing"; fail=$((fail+1)); }

echo "$pass passed, $fail failed"
[ "$fail" = 0 ] || { echo "---- output ----"; printf '%s\n' "$out"; exit 1; }
