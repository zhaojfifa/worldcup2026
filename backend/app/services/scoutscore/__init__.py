"""ScoutScore v0.1 — hybrid factor scoring + (LLM-ready) reasoning, historical-replay mode.

Builds a **prediction accountability** loop from a cached Scout Pack:
pre-match model view (replay) → actual result → hit/miss/partial → factor
validation → missed factors → model correction → operator recap copy.

NOT a real archived prediction. NO real win probability, no SHAP, no xG, no
betting/odds, no injury inference. The reasoning layer is deterministic/template
(AI_PROVIDER=mock fallback); DeepSeek/Gemini are the designated production
reasoning models behind the existing draft-only, forbidden-filtered path.
"""
from app.services.scoutscore.factors import compute_factor_scores  # noqa: F401
from app.services.scoutscore.accountability import (  # noqa: F401
    build_replay,
    build_accountability_report,
)
