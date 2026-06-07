#!/usr/bin/env bash
# Myanmar mobile QA screenshots (headless Chrome). Temporary QA helper — not part
# of the production build. Requires a running dev server (default :4321).
#
# Usage: bash scripts/qa/mm_mobile_shots.sh [BASE_URL] [OUT_DIR]
set -euo pipefail

BASE="${1:-http://localhost:4321}"
OUT="${2:-docs/qa_screenshots/mm_mobile}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p "$OUT"

shot() { # path lang w h file
  local path="$1" lang="$2" w="$3" h="$4" file="$5"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size="${w},${h}" \
    --virtual-time-budget=4500 \
    --screenshot="$OUT/$file" "${BASE}${path}?lang=${lang}" >/dev/null 2>&1
  echo "saved $file"
}

# Myanmar — 390x844 and 430x932
for pair in "/:home" "/detail:detail" "/token:token" "/community:community"; do
  p="${pair%%:*}"; n="${pair##*:}"
  shot "$p" mm 390 844 "${n}-mm-390.png"
  shot "$p" mm 430 932 "${n}-mm-430.png"
done

# Regression — Vietnamese & Chinese home
shot "/" vi 390 844 "home-vi-390.png"
shot "/" zh 390 844 "home-zh-390.png"

echo "done"
