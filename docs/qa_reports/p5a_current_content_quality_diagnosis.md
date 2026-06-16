# P5A · Phase 0 — Current Content-Quality Diagnosis

> Branch `feature/mvp2-p5a-core-1p2-content-quality`. Mechanism (P4R++) is solid; this diagnoses why
> the COPY still reads weak. Grounded in the live DOM + the bundled artifacts.

1. **Why weak after source-of-truth fixed?** The pipeline now renders the reviewed copy, but the
   reviewed copy itself is generic/hedgy and lacks a punchy hook, a concrete data-tied reason, a named
   pressure point, and a group hook. Correct content, unpersuasive wording.
2. **Generic lines still present:** `主推` leans open with the FORBIDDEN "赛前倾向…" (2 of 3 artifacts);
   `why` is high-level ("实力与状态领先") without a specific number; risk is a bare label ("中").
3. **Prediction fields rendered but not persuasive:** main_lean (hedged), why (generic), risk_level
   (bare token), top_variable (ok). No hook_headline, no pressure_point, no tactical_watch, no
   confidence_language, no group_hook.
4. **Recap fields rendered but not useful enough:** observation has assessment/deviation/next_impact
   but no explicit `result_judgment` label, no separated `what_was_right` / `what_was_wrong` /
   `model_correction`, no `next_match_learning`.
5. **From reviewed LLM JSON:** main_lean, primary_score, backup, risk_level, risk_note, top_variable,
   why, tactical_read, risk_factors, external_expectation, t30_checklist, share_copy (synced to i18n.zh).
6. **Authored static copy:** the CHROME labels (UI chrome), the FocusBlock frames (manual fallback),
   the recap OBSERVATION chrome — all static (acceptable as chrome, not the judgement).
7. **Should be LLM but still effectively generic:** the lean/why/risk wording — present but weak;
   needs the v2 contract (hook/reason/pressure/risk/watch/group/share), no forbidden phrases.
8. **Minimum stronger contract (1 primary + 2 secondary):** see docs/specs/p5a_llm_copy_contract_v2.md.
9. **Homepage vs detail:** homepage primary = hook_headline + lean + exact score + one main reason +
   hidden risk + CTA; secondary cards = lean + score + one reason + one risk + watch tag; recap card =
   result_judgment + predicted-vs-actual + right/wrong/correction + CTA. Detail (/predict, /recap) =
   the full v2 set.
10. **Guard so weak copy can't pass:** rendered-DOM guards that FAIL on forbidden phrases + missing
    hook/reason/risk/watch/share/source-label + secondary-as-schedule-row + OBSERVATION-as-full-recap.
