# MVP2-P3 Status

Sprint: Hotspot Prediction First Product Path
State: IMPLEMENTING
Branch: feature/mvp2-p3-hotspot-prediction-first
Current HEAD: f234531 (branch base)
Target deploy commit: (set in FINAL_REPORT after implementation)
Live bundle: last known index-Dz95Uq3Y.js (P1.5b) — NOT updated by this sprint
Runtime fixture date: 2026-06-14 (frontend/public/data/daily-fixtures.json + backend runtime manifest)
Send status: HOLD

## Current product truth

Homepage product loop is driven by `selectProductLoop` over the runtime daily-fixtures
manifest (backend → static → bundled fallback). The 2026-06-14 slate:

- featuredRecap  = first finished = **Brazil 1-1 Morocco** (1489371, RECAP_PENDING, recapReady=false)
- featuredPrediction = first scheduled = **Netherlands vs Japan** (id=null, manual fixture)
- otherRecaps   = [Mexico 2-0 South Africa (1489369, RECAP_READY)]
- secondarySchedule = Germany/Curacao, Ivory Coast/Ecuador, Sweden/Tunisia, Australia/Turkey

### Drift identified (Owner verdict)
The funnel priority is wrong: the homepage rendered **昨日热点复盘 (recap) FIRST**, then
今日热点预测 (prediction). Hotspot prediction must always be first. Additional gaps:
- Netherlands prediction card had NO tactical-room CTA (gated on `id && renderable`, both false
  for the manual fixture) → today's hotspot was effectively buried.
- No copy/share entry on the lead prediction card or the recap card.
- /predict/<manual fixture> rendered a near-blank "sample not available" placeholder.
- Recap card had no link to the safe observation page when recapReady=false.

## P0 blockers

- P0-1 homepage lead must be 今日热点预测 (currently 昨日热点复盘 leads)
- P0-2 Netherlands card needs 进入战术室 + 加入临场情报群 + 复制/分享入口
- P0-3 Brazil recap second + link to safe observation page
- P0-4 /predict for today hotspot must work without full narrative (fallback tactical room)
- P0-5 /recap for Brazil must be safe observation when recapReady=false (already shipped f234531; verify)
- P0-6 no fake recap, no generation wording, no betting vocabulary

## P1 deferred

richer generated tactical narrative · advanced model visualization · automated LLM generation ·
share-card visual polish · language polish · scoring/ranking automation.

## Next action

Implement Phases 3–4 (minimal frontend reorder + fallbacks + share buttons + guard), run checks,
fill FINAL_REPORT. No deploy, no send.

Last updated: 2026-06-14 (engineering, MVP2-P3 thread)
