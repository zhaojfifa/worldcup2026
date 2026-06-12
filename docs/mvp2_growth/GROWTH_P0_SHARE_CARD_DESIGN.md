# Growth P0 — Share-Card Design (design-only)

> Branch feature/mvp2-growth-p0-design @ main 6b56725. NO runtime in this P0: cards are produced as
> SCREENSHOTS of existing live surfaces (or operator-cropped images of them), shared manually.
> Every judgement string on a card is a guard-passed LLM field — operators never rewrite copy.

## 1. Card A — 1489371 pre-match strong-call card

Source surface: `https://worldcup2026-izid.onrender.com/predict/1489371?lang={zh|vi|my}` — the
StrongCallCard block (already live, scanner-clean).

Structure (top→bottom):
1. Brand row: Giành Cup · persona name (俅哥说球 / Tiên Tri Bóng Đá / Football Oracle)
2. Fixture row: 🇧🇷 Brazil vs Morocco 🇲🇦 · kickoff local time · MetLife
3. 俅哥主看 — LLM `main_lean`（「赛前倾向巴西胜，但冷门风险偏高」）
4. 赛前参考比分 — LLM `scoreline_view`（「俅哥给出的赛前参考区间：2-1、1-1、2-2」）
5. 冷门风险 — LLM `risk_level`
6. 最大变量 — LLM top watch signal（「首发11人（开球前30分钟）」）
7. 外部预期 block — projected lines only（外部预期偏向巴西…以官方首发为准）
8. Hook line: 赛前看方向，临场看变量 + group CTA text（see CTA pack §2）
9. Footer: disclaimer line（历史表现不代表未来结果…）— MUST stay in frame

Copy examples (existing guard-passed artifacts, quoted verbatim):
- zh short hook:「巴西vs摩洛哥：冷门密码已浮现」
- vi: “Brazil vs Morocco: Tiên Tri nói gì?”
- my: “Brazil vs Morocco: Oracle ရဲ့ ပွဲကြိုအမြင်”

## 2. Card B — 1489369 recap trust card

Source surface: `/recap/1489369?lang={…}` hero + scoreline block.
Structure: fixture + final score 2-0 → LLM `screenshot_line`（zh:「赛前参考区间1-1/1-0/0-1，
实际2-0——方向对，但比分被红牌放大」· vi: “bàn thắng thứ hai đến khi đã hơn người từ phút 49…”）
→ trust line label 赛后看校准 → group CTA → disclaimer.
Why this card: it is the accountability proof — archived judgement vs honest outcome. It is the
card that differentiates us from pick-selling accounts.

## 3. CTA wording (safe set — fixed, from live surfaces)
zh: 进群看完整版 / 加入情报群，等临场修正 · vi: Vào nhóm xem bản đầy đủ · my: အဖွဲ့ထဲ ဗားရှင်းအပြည့် ကြည့်ရန်.
Link is pasted by the operator OUTSIDE the image (no URL inside the card; no QR in P0).

## 4. Forbidden on any card
赔率/盘口/投注/博彩/下注/庄家/让球/大小球/跟单 · kèo/cửa trên/cửa dưới/nhà cái/cá cược/tài xỉu ·
betting/odds/handicap/bookmaker/bet slip/wager · လောင်းကစား family · 稳赚/必中/包赢/win guarantees ·
percentages presented as win probability · 模型/AI-process words · source names/prices/bookmakers ·
sha256/artifact/guard/mock · any reward/commission/recharge wording · player-name injury claims not
confirmed by official XI（keep 锋线核心是否首发）.

## 5. Allowed vs not-allowed data fields
ALLOWED: persona lean, reference scoreline band, risk level + reason, top variable name, projected
external-expectation lines, kickoff/venue/round, final score + honest band comparison (recap),
red-card minute facts, disclaimer.
NOT ALLOWED: odds/prices/implied %, bookmaker/source names, internal factor keys, missing-data
audit phrasing, unconfirmed injuries/ages/workloads, MTC/reward incentives for sharing.

## 6. Screenshot layout recommendation
Mobile 390px width · crop = one card per image (strong card OR recap hero, not full page) ·
keep persona name + disclaimer visible in every crop · zh/vi/my shot per send target ·
file naming: `docs/qa_screenshots/mvp2_trial_sends/sharecard_{fixture}_{surface}_{lang}_{date}.png`.

_No runtime: no share button, no card-generator endpoint, no QR. Owner GO required before any card
is sent anywhere._
