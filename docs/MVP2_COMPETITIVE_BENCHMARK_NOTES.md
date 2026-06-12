# MVP-2 Competitive Benchmark Notes (internal only)

> Product Closure Sprint P1 (2026-06-12). Purpose: name what prediction/gaming-style products do
> well — and adopt the FORM, never the betting mechanics. This note authorizes NOTHING in Track B;
> it is a copy/IA reference for the strong-judgment Track A loop only.

## What to learn (form, all already mapped to our surfaces)

| Pattern they do well | Our compliant equivalent | Where it lives now |
|---|---|---|
| Strong headline with a position | LLM `hero_title`/`short_title` with a stated lean | home hero hook, predict hero |
| Clear pick, stated up front | 俅哥主看 + `main_lean` first row of the strong card | StrongCallCard on /predict |
| Scoreline range, not single-score bravado | 赛前参考比分 (`scoreline_view`, band of 2-3 scores) | strong card row 2 |
| Risk label on every pick | 冷门风险 (`risk_level` with a reason) | strong card row 3 |
| Market expectation direction | 外部预期/公开倾向 projection — direction only, no prices | strong card 外部预期 block |
| Expert consensus framing | 公开预测更看好X，但… (recorded signal, named sources internal) | projection line 2 |
| Late team-news update as THE retention hook | 30 分钟临场修正 (赛前看方向，临场看变量) | RescoreHookCard + #rescore block |
| Social proof | post-match recap as receipts: 方向对了/比分被红牌放大, archived & hash-verified | RecapAnchorCard → /recap/1489369 |
| Shareable one-liner | LLM `screenshot_line` / `social_post` | send-kits, recap cards |
| Group/community hook | 进群等临场修正 / 群内完整版 | every CTA pair |

## What NOT to copy (hard compliance lines — all guard/scanner enforced)

odds tables · bet slips · handicap tips (亚盘/让球/大小球/kèo/cửa trên-dưới) · bookmaker links or
names on customer surface · recharge/commission/agent hierarchy · payout/cash-out · win guarantees
(稳赚/必中/包赢) · implied-probability percentages presented as hit-rate promises.

## The differentiator we have that they don't

Betting-style products sell the pick; they never show their misses. Our loop's trust engine is the
**archived, hash-verified pre-match judgement + honest recap** (2-0 was OUTSIDE the band; the red
card pushed it out). Accountability is the moat — keep recaps honest or the whole loop is generic.

_Internal note only. No Track B runtime is authorized by this document._
