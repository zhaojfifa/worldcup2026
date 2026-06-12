# MVP-2 Track A · A4 First REAL Post-Match Recap — Product Review

> Fixture **1489369 Mexico 2-0 South Africa** (WC2026 opener, Estadio Azteca, FT 2026-06-11).
> First production run of the A4 real_recap loop on a finished fixture with REAL archived
> pre-match artifacts. Date: 2026-06-12. Branch `feature/mvp2-api-football-ingestion`. PR #3 Draft.
> Operation paused · small private trial only · nothing sent · sends = operator manual + Owner GO.

## 1. What ran (engineering evidence)

| Step | Result |
|---|---|
| Fixture truth (API-FOOTBALL) | `Match Finished`, final 2-0 home, lineups/events/stats/players ingested; injuries=0 rows (flagged missing, never inferred) |
| Scout pack refresh | `docs/data_audit/mvp2_scout_pack_samples/1489369.json` coverage 100%, missing=['injuries'] |
| real_recap frame | `docs/data_audit/mvp2_scoutscore_v0_2/1489369.real_recap.factor_frame.json` — `prematch_provenance` cites all 3 archived narratives (path + sha256 + generated_at, committed pre-kickoff) |
| Narratives | 3/3 real DeepSeek (zh r20260612T0028Z · vi/my r20260612T0005Z), all guard_passed; zero mock |
| Queue | 3 guard_passed recap items; 4 zh supersedes (honest history); 6 prematch items auto-expired at kickoff |
| Send-kit | `docs/data_audit/mvp2_send_kits/1489369.recap.md` (NEW A4 kit step — quotes guard-passed LLM fields verbatim; [群链接由运营填写]; approve + Owner GO required) |
| Frontend | `/recap/1489369` renders real_recap via ProductRecapView; `/predict/1489369` now redirects there (pre-match room is over); build PASS |
| Visible-copy scan | extended to 18 surfaces (+/recap/1489369 ×3) — **18/18 PASS** local prod build |
| Screenshots | `docs/qa_screenshots/mvp2_tracka_a4_recap/` (home zh, recap zh/vi/my, predict redirect) |

## 2. REAL findings this run (both fixed pipeline-level, never hand-edited)

1. **zh scoreline overclaim** — DeepSeek wrote「实际比分2-0，在合理区间内」against an archived
   band of 1-1/1-0/0-1. Exactly the dishonesty class A4 exists to prevent. Fixed: new guard rule
   `real_recap scoreline overclaim` (parses the band vs the claimed actual score, negation-aware:
   「不在区间内」/“nằm ngoài khoảng” stay legal) + prompt scoreline-honesty section; zh regenerated
   until honest:「实际2-0不在区间内，但方向正确」.
2. **zh banned n-grams** — 「但过程**验证了**」 trips the visible scanner's literal「过程验证」ban;
   「盲区」persisted in factor names across retries. Fixed: guard zh de-model list now mirrors
   `check_customer_visible_copy.py` (过程验证/数据缺失/缺数据/自证 added in BOTH checkers) and the
   zh prompt bans the literal n-gram with rewrite guidance (比赛走势印证了). Same lesson as the
   De-Modeling sprint: retries don't converge until the PROMPT says it.

## 3. Product review (Owner's 7 questions)

1. **Useful to fans?** Yes, more than the pre-match page: it closes the loop — what 俅哥 said
   (quoted from the archive), what the 90 minutes showed (16射4正 vs 3射2正, 61% possession),
   what was right (risk framing, efficiency variable), what was missed (Mexico's control was
   under-weighted). It reads as accountability, not news.
2. **Strengthens persona trust?** Yes — the strongest line is honesty about the scoreline:
   「方向对了但比分没在区间内」. A persona that admits the band missed 2-0 is more credible than
   one that claims credit. vi independently wrote the same honesty (“nằm ngoài khoảng”).
3. **Reason to join the group before the next match?** Yes — every语言 ends on the same hook:
   the three variables that decided this match (XI / GK / finishing efficiency) are exactly what
   the 30-min pre-kickoff re-check covers for 1489371. The recap is the advertisement for A3.
4. **AI/model/process flavor on customer surface?** None visible — 18/18 scan PASS; model/provider/
   sha256/provenance live only in the collapsed internal fold. Customer reads a football analyst.
5. **Honest about misses?** Yes — under-weighted factors are explicit (Mexico's possession
   dominance, South Africa's attacking impotence), and the scoreline miss is stated plainly.
6. **Is the 30-min correction hook stronger post-match?** Yes — pre-match it was a promise;
   post-match it is evidence: the variables 俅哥 flagged as「开球前30分钟要重看」are provably the
   ones that decided the match. The recap makes the hook empirical.
7. **Improve before next fixture (1489371):**
   - Home hero CTA still reads「进入俅哥战术室」while pointing at a recap — label should switch
     per mode (small dict change, next round).
   - Hero card should promote the NEXT fixture (1489371) once its A2 is re-verified, with the
     1489369 recap as the trust anchor below.
   - my recap scoreline_view states the band but not the comparison — prompt could ask for the
     same explicit honesty line as zh/vi.
   - Quota ledger still under-counts subprocess API calls (P1, pre-existing).

## 4. Compliance check

No betting/odds/handicap/casino wording (guard + scan). No payment/token. No auto-send — kit is
file-only; queue blocks mark-sent without channel+group+screenshot; sends need Owner GO. Track B
untouched (no referral runtime). Engineering wrote zero narrative text — all customer copy is
guard-passed DeepSeek output quoted verbatim.

## 5. Verdict (engineering self-assessment)

A4 loop = **PASS** end-to-end on a real finished fixture. Final PASS = Owner review of this doc +
screenshots + send-kit. Live trial sends remain blocked on the Render SPA rewrite (deep links 404
live) — operator action, see deploy section of the thread report.
