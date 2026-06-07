#!/usr/bin/env bash
# Customer-language mobile QA screenshots (headless Chrome). Temporary QA helper —
# NOT part of the production build. Requires a running dev server (default :4321).
#
# Usage: bash scripts/qa/lang_mobile_shots.sh [BASE_URL]
# Captures mm → docs/qa_screenshots/mm_mobile/, vi → docs/qa_screenshots/vi_mobile/,
# plus zh regression home shots, at 390x844 and 430x932.
set -euo pipefail

BASE="${1:-http://localhost:4321}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

shot() { # path lang w h outdir file
  local path="$1" lang="$2" w="$3" h="$4" outdir="$5" file="$6"
  mkdir -p "$outdir"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size="${w},${h}" \
    --virtual-time-budget=4500 \
    --screenshot="$outdir/$file" "${BASE}${path}?lang=${lang}" >/dev/null 2>&1
  echo "saved $outdir/$file"
}

for lang in mm vi; do
  out="docs/qa_screenshots/${lang}_mobile"
  for pair in "/:home" "/detail:detail" "/token:token" "/community:community"; do
    p="${pair%%:*}"; n="${pair##*:}"
    shot "$p" "$lang" 390 844 "$out" "${n}-${lang}-390.png"
    shot "$p" "$lang" 430 932 "$out" "${n}-${lang}-430.png"
  done
done

# zh regression (home only, both viewports)
shot "/" zh 390 844 "docs/qa_screenshots/mm_mobile" "home-zh-390.png"
echo "done"
