#!/usr/bin/env bash
# Vietnamese mobile QA RECHECK screenshots (headless Chrome). Temporary QA helper —
# NOT part of the production build. Requires a running dev server (default :5173).
#
# Recheck of the FULL vi customer path using the Myanmar QA standard — crucially adds
# /report (the page that was the Myanmar root cause) which the original vi sweep omitted.
#
# Usage: bash scripts/qa/vi_mobile_recheck_shots.sh [BASE_URL]
# vi → docs/qa_screenshots/vi_mobile_recheck/ at 390x844 and 430x932,
# plus mm + zh regression home/report shots at 390x844.
set -euo pipefail

BASE="${1:-http://localhost:5173}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="docs/qa_screenshots/vi_mobile_recheck"
mkdir -p "$OUT"

shot() { # path lang w h file
  local path="$1" lang="$2" w="$3" h="$4" file="$5"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size="${w},${h}" \
    --virtual-time-budget=4500 \
    --screenshot="$OUT/$file" "${BASE}${path}?lang=${lang}" >/dev/null 2>&1
  echo "saved $OUT/$file"
}

# vi full customer path (Home / Detail / Report / Community / Token) — both viewports.
for pair in "/:home" "/detail:detail" "/report:report" "/community:community" "/token:token"; do
  p="${pair%%:*}"; n="${pair##*:}"
  shot "$p" vi 390 844 "${n}-vi-390.png"
  shot "$p" vi 430 932 "${n}-vi-430.png"
done

# Regression — mm (home + report) and zh (home) at 390x844.
shot "/"       mm 390 844 "home-mm-regression-390.png"
shot "/report" mm 390 844 "report-mm-regression-390.png"
shot "/"       zh 390 844 "home-zh-regression-390.png"
echo "done"
