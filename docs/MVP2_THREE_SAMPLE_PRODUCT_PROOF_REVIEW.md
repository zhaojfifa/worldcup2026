# MVP-2 — Three-Sample Product Proof Review (acceptance report)

> **Date:** 2026-06-11 · **Sprint:** LLM-Driven Product Proof (`MVP2_LLM_DRIVEN_PRODUCT_PROOF_PLAN.md`)
> · **Branch:** `feature/mvp2-api-football-ingestion` · **PR #3: still Draft** · **Operation: still paused.**
> Verdict: **Engineer self-verify PASS** — final PASS requires Owner review of this doc + screenshots.

## 1. The three samples (all shipped)

| Sample | Page | Narrative (main view) | Mode |
|---|---|---|---|
| A 爆冷复盘 Argentina 1–2 Saudi Arabia (`855737`) | `/recap/855737` | DeepSeek zh/vi, guard-passed | `historical_recap` |
| B 决赛拉锯 Argentina 3–3 France pens (`979139`) | `/recap/979139` | DeepSeek zh/vi, guard-passed | `historical_recap` |
| C 2026 赛前建模 Brazil vs Argentina | `/predict/2026-brazil-argentina` | DeepSeek zh/vi, guard-passed | `pre_match_2026_modeling` |

979139 data was available → fallback 855741 **not needed**. Pipeline per plan §0:
factor frame (`mvp2_build_scoutscore_v0_2_factors.py`) → LLM input → DeepSeek/Gemini →
guard → page render → ops/CTA copy (LLM) → this review.

## 2. Acceptance checklist (16 items)

1. **两个历史复盘完成** ✅ A+B live at `/recap/{855737,979139}` (zh/vi).
2. **2026 赛前建模样例完成** ✅ `/predict/2026-brazil-argentina` (lean / scoreline band / risk level /
   key factors / live-30min re-score / free-vs-full / CTA / internal fold / disclaimer).
3. **真实数据源** ✅ API-FOOTBALL Scout Packs 855737+979139 (lineups, formation, coach, events
   timeline, team/player statistics, source_ledger); local Kaggle internationals CSVs (49k rows,
   through 2026-06) → **derived Elo** (K=32, +60 home, snapshots at match eve), last-10 form, H2H,
   shootout history, recent scorers; real 2026 group schedules (from the same dataset).
4. **assumption_context 补足（标记，未伪装）** ✅ injuries/suspensions · xG · squad market value ·
   official FIFA rank · 2026 lineups/GK/tactics · knockout venue/travel · **Brazil–Argentina 2026 是
   假想淘汰赛相遇**（factor frame `hypothetical_fixture: true`，narrative `internal_notes` 披露，客户
   文案一律「若两队在淘汰赛相遇」）。主视图把缺口写成「赛前需重点跟踪的变量」。
5. **DeepSeek + Gemini 双生成** ✅ 12 files (3 samples × zh/vi × 2 providers), **all real LLM, zero mock**
   (`docs/data_audit/mvp2_product_proof_narratives/`).
6. **默认 provider 推荐** ✅ **DeepSeek default, Gemini benchmark** — re-validated on all 3 samples
   (`MVP2_LLM_NARRATIVE_PROVIDER_REVIEW.md` 2026-06-11 section).
7. **Narrative guard** ✅ `check_mvp2_product_narrative_guard.py` **12/12 PASS**. Guard caught & we fixed:
   vi 盘口黑话 (kèo / lật kèo / cửa trên / cửa dưới, 5 files), invented `t.me` URL (1 file), missing
   per-factor provenance (2 Gemini files), AI-filler tone (1 Gemini retry), DeepSeek vi truncation
   (max_tokens 3000→4500).
8. **页面渲染 LLM narrative** ✅ main view = narrative JSON only (`ProductProofViews.tsx`); engineering
   contributes section labels / buttons / fold frames. en/mm = deterministic fallback (no fake narrative).
9. **订阅 / 入群 CTA** ✅ LLM `group_join_copy` + `subscription_hook` + `today_cta` rendered as CTA
   cards/buttons (→ `/community`, `/`); predict has the free-vs-full frame; recap has 入群 + 今日观点 CTA.
10. **无 AI 味 / 无工程审计味** ✅ guard bans filler (综上所述/值得注意的是/nhìn chung…), audit tokens
    (MISS/replay/assumption/snake_case keys), research tone, journalism-only titles; spot-checks read
    as product copy (e.g. zh hero「369分Elo差距翻车：ScoutScore赛前该在哪三处看见沙特冷门」).
11. **zh / vi 截图** ✅ `docs/qa_screenshots/mvp2_product_proof/{recap_855737_zh,recap_855737_vi,
    recap_979139_zh,recap_979139_vi,predict_2026_brazil_argentina_zh,predict_2026_brazil_argentina_vi}.png`
    (390×844@2x, dev server). Deep sections text-verified in DOM (CTA/disclaimer/fold/est-badge present ×6).
12. **vi Han check** ✅ narrative JSON: 0 Han (guard, whole-file). Rendered pages: the 3 surfaces add
    **0** Han; a **pre-existing** 22-char zh residual lives in the internal-preview shell chrome (header
    brand line/nav badges — identical count on `/` and `/community`, predates this sprint). Logged as a
    branch-level layout-localization backlog item, NOT a product-proof surface regression.
13. **Forbidden scan** ✅ guard betting/guarantee list (zh/vi/en incl. kèo/cửa trên/nhà cái) + repo grep
    over new surfaces: clean. No 提现 outside 不可提现. Disclaimers rendered on all 3 pages.
14. **Build / test** ✅ `tsc -b && vite build` PASS; zh home regression OK; 0 console errors on the 4
    checked pages; guard exit 0.
15. **PR #3 仍 Draft** ✅ verified via `gh pr view 3` (isDraft=true, OPEN) — never marked ready/merged.
16. **Operation 仍 paused** ✅ no public surface, no channel post, payment/Token untouched,
    `public_ready` unchanged.

## 3. Provider note (summary)

DeepSeek: 球迷语感与可截图感更强（「翻车」「冷门密码」「cơn lốc Mbappé」）、风险因子更密（5–6 条 vs 3–4）、
ops copy 更短更带数字；vi 自然。Gemini：结构更稳、订阅话术更完整但偏长偏推销（“洞察先机！”）、需要更多
retry（溯源缺失/黑话）。两者初稿都会写 vi 盘口黑话——**guard 是必须层，不是保险层**。

## 4. Known issues / follow-ups (not blocking this proof)

- Internal-preview shell chrome 22 Han chars on vi (pre-existing; layout localization backlog).
- `main_lean` 与 `risk_level` 偶有语气差（「冷门风险偏高」vs「中」）— 模型措辞自由度内，后续 prompt 可加一致性约束。
- Evidence pages for 979139 / 2026 not extended (855737 evidence link kept) — optional polish per plan.
- Live deploy still needs the Render dashboard SPA rewrite (pre-existing operator step) before deep links work in prod.
- Stray local file `docs/qa_screenshots/mvp2_evidence_board_v2/recap_855737_zh_llm_副本.png` (untracked, not ours) left untouched.

## 5. Compliance

不博彩 · 不现金投注 · 不承诺命中/收益 · 无胜率/命中率话术（仅真实比赛统计数字）· 比分区间一律「模型估计」·
MTC 未触碰 · 每页带「历史表现不代表未来结果，仅供数据分析和球迷娱乐参考」。
