# Day 5 — Frontend / Backend Alignment

> Day 5 Phase A delivers a **frontend prototype only**. The backend is
> **unchanged** (no code, no tables, no API shape changes). This document
> records how the new frontend modules map to existing data, what the frontend
> derives locally, and the future Phase B/C backend contract those derivations
> are designed to migrate onto without breaking changes.

---

## 1. New frontend modules ↔ existing API data

| Frontend module (Day 5) | Backed by existing API | Notes |
|-------------------------|------------------------|-------|
| 今日 AI 最强信号 (C-pick) | `GET /api/v1/matches` | C-pick chosen client-side: prefer `tag=focus`, else max `confidence` |
| 今日比赛简表 | `GET /api/v1/matches` | time / teams / win_prob / risk_level / tag — all existing |
| 今日爆冷风险 TOP3 | `GET /api/v1/matches` | ranked by frontend-derived `upset_score` |
| AI 情报战绩 | — (none) | status surface only：「真实赛果回灌后开放」+ disclaimer |
| 社区热门选择 | partial (`tag`) | light status surface：「社区热度即将上线」 |
| Token / 连胜挑战 / 排行榜入口 | Token via existing token endpoints | ranking entry is a placeholder pending data |
| 详情页 AI 结论卡 | `GET /api/v1/matches/{id}` | tendency/stars/risk derived; exact score stays locked (paid) |
| 详情页 为什么 / 风险维度 | `matches/{id}` + (on report) `reports/{id}` | reasons from `features[]` when present, else rule fallback |

**No existing endpoint was modified.** Frontend continues to consume
`/matches`, `/matches/{id}`, `/reports/{id}` exactly as before, in both
`VITE_USE_MOCK=true` and `false`.

---

## 2. Fields derived by the frontend ops layer (`src/ops/derive.ts`)

All derived purely from existing `Match` / `Prediction` / `Report` fields
(`win_prob`, `confidence`, `risk_level`, `risk_note`, `free_note`, `tag`,
`features`). No new backend field is required.

| Derived field | Source | Rule summary |
|---------------|--------|--------------|
| `ai_pick_label` | win_prob | 主胜偏强 / 客胜偏强 / 主队不败趋势 / 难分胜负 … |
| `confidence_star` | confidence | ≥72→5★, 60–72→4★, 50–60→3★, 40–50→2★, else 1★ |
| `upset_score` | risk_level + prob spread + tag + confidence | 0–100 |
| `risk_tags` | risk_note / free_note keyword categories | category chips, never fabricated facts |
| `top_risk` | risk_note (first clause) | one-line |
| `free_conclusion` | label + stars | no exact score |
| `premium_teaser` | static | what unlock reveals |
| `heat_label` | tag / confidence | lightweight, non-fabricated |
| `live_sensitive_score` | risk_level + tag | 0–100 |
| `reason_bullets` | features[] if present, else win_prob/confidence/risk | 2–3 short, data-observation bullets |

These are intentionally named to match the **future backend `ops_output`**
(§4) so the migration is a drop-in.

---

## 3. Fields that should later be served by the backend (`home/summary`)

When Phase B lands, the home page should fetch one aggregate instead of
deriving everything client-side. Target (Phase B, **not implemented in Day 5**):

```
GET /api/v1/home/summary
{
  "top_pick":       { match + ai_pick_label + confidence_star + top_risk },
  "today_matches":  [ MatchListItem … ],          // existing shape, reused
  "upset_alerts":   [ { match, upset_score, hook } ],
  "performance":    { yesterday_hit, yesterday_total, last7d_rate, disclaimer },
  "community_heat": { most_followed, hot_discussion, pick_split }
}
```

- `top_pick`, `today_matches`, `upset_alerts` → **derivable today** from
  `Match`/`Prediction` (currently done in the frontend ops layer; moves to the
  backend in Phase B for consistency + fewer client round-trips).
- `performance`, `community_heat` → require new data (see §4); until then the
  frontend renders the「待真实赛果回灌 / 数据能力建设中」status surfaces.

---

## 4. Fields that need new tables (Phase B/C — not now)

| Future table | Powers | Status |
|--------------|--------|--------|
| `MatchResult` | 真实赛果与战绩统计（performance/daily） | not created |
| `MatchEngagement` | 社区热度（community/heat） | not created |
| `UserStreak` | 连胜 / 积分挑战排行（rankings） | not created |

All three are **independent of the prediction core**; adding them will not
touch `Match` / `Prediction` / `Report`.

---

## 5. Non-breaking guarantees (verified in Day 5)

- `GET /api/v1/matches` — **unchanged**, consumed as-is.
- `GET /api/v1/matches/{id}` — **unchanged**.
- `GET /api/v1/reports/{id}` — **unchanged**.
- `VITE_USE_MOCK=true / false` dual mode — **preserved** (both verified).
- `client.ts` interface contract — **untouched**.
- `transform.ts` — extended only with the existing field mappers; no change to
  how existing fields are mapped (the new derivations live in `ops/derive.ts`,
  not in `transform.ts`).
- baseline predictor / backend / Render config / LLM / R2 — **untouched**.

---

## 6. Phase boundaries recap

- **Phase A (Day 5, done):** frontend IA upgrade on existing data + local
  derivations + status surfaces for not-yet-available data.
- **Phase B (later):** `home/summary`, `MatchResult` + 赛果回灌,
  `performance/daily`, `upsets/today`, `community/heat`.
- **Phase C (later):** LLM `reason_bullets`/premium narrative + compliance
  filter, `rankings`/`UserStreak`, share cards, R2, i18n (VN→MM), social
  conversion helpers.
