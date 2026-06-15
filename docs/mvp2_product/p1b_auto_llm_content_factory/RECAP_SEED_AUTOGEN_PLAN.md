# P1B · RECAP_SEED_AUTOGEN_PLAN

> Every generated prediction draft carries a `recap_seed` — one line linking the pre-match call to
> what the post-match recap must verify. This is what makes the recap GROUNDED instead of invented.
> Enforced by `check_recap_seed_grounding.py`.

## What recap_seed is
A pre-match sentence that names: the predicted call (primary_score), and the specific things the
recap should check after full-time (was the call met? what was the deviation? did the opponent's
counter exceed the pre-match read?). It must REFERENCE `primary_score` (grounding) and must NOT
assert a fabricated match event (no "第 X 分钟 进球" claims in a pre-match seed).

## After final score (recap generation)
```
prediction artifact + recap_seed + actual_score
 → if event data (lineups/events/player stats) MISSING → OBSERVATION_READY (receipt only; recap_ready=false)
 → if enough data exists                               → RECAP_READY draft (full tactical_review)
 → NEVER fake event claims; NEVER a full recap without real data
```
The recap prompt/reviewed/artifact flow (P1) lives in `docs/data_audit/mvp2_recaps/{prompts,reviewed}/`
+ `frontend/src/data/recapArtifacts/`. The recap_seed feeds the recap prompt's "pre-match call" block.

## Grounding rule (guarded)
- `recap_seed` non-empty.
- `recap_seed` contains the predicted `primary_score` (call → recap link).
- No fabricated-event regex match (`第 N 分钟 … 进球/破门/红牌/点球`).
- A finished fixture's recap artifact must not mislabel OBSERVATION_READY as `recap_ready=true`.

## This sprint
Both live DeepSeek drafts carry a grounded recap_seed referencing the predicted score (e.g.
Belgium-Egypt: "赛后核对：主推 1-0 是否兑现…"). 1489371 Brazil-Morocco stays OBSERVATION_READY (full recap
blocked — no event data ingested), consistent with the recap contract.
