from __future__ import annotations
"""
R4 — runtime CONTENT store (Owner GO 2026-06-16: remove the daily frontend-deploy dependency).

Stores the daily CONTENT package an operator uploads (key 'runtime_content_current') so the live
frontend can read prediction / recap / selectedHotspot content at runtime — bundled content becomes
fallback only, and a daily content cutover no longer needs a frontend rebuild/deploy.

The package is OPAQUE product content (selectedHotspot + prediction artifacts + observation artifacts
+ optional share copy), exactly the shapes the frontend already renders. No score/probability is
invented here; this layer only stores and serves what the cutover (gate-passed) produced.

COMPLIANCE: public product content only — NO user/payment/attribution data. Reuses the existing
runtime_manifests key/value table (additive key; NO schema migration). send_status stays HOLD.
"""
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.runtime_manifest import RuntimeManifest

CURRENT_KEY = "runtime_content_current"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_package(pkg: dict) -> dict:
    """Keep the package shape the frontend expects; stamp store time. Never invents content."""
    return {
        "date": pkg.get("date") or pkg.get("generated_for_date"),
        "generated_at": pkg.get("generated_at") or pkg.get("captured_at"),
        "source_mode": pkg.get("source_mode", "api-football"),
        "send_status": "HOLD",
        "selectedHotspot": pkg.get("selectedHotspot"),
        "predictions": pkg.get("predictions") or {},
        "observations": pkg.get("observations") or {},
        "shares": pkg.get("shares") or {},
        "lifecycle": pkg.get("lifecycle"),
    }


def upsert_current(db: Session, pkg: dict, by: str | None) -> dict:
    stored = normalize_package(pkg)
    stored["stored_at"] = _now().isoformat()
    row = db.get(RuntimeManifest, CURRENT_KEY)
    payload = json.dumps(stored, ensure_ascii=False)
    if row:
        row.value_json = payload
        row.updated_at = _now()
        row.updated_by = by
    else:
        db.add(RuntimeManifest(key=CURRENT_KEY, value_json=payload, updated_at=_now(), updated_by=by))
    db.commit()
    return stored


def get_current(db: Session) -> dict | None:
    row = db.get(RuntimeManifest, CURRENT_KEY)
    if not row:
        return None
    try:
        return json.loads(row.value_json)
    except Exception:
        return None


def assemble_response(db: Session, date: str | None = None) -> dict:
    """Public GET payload. Empty-but-valid when nothing stored (frontend then uses bundled fallback);
    never 500s. With a date filter, only returns the package if its date matches (else empty)."""
    stored = get_current(db)
    if not stored or (date and stored.get("date") != date):
        return {"date": None, "generated_at": None, "source_mode": None, "send_status": "HOLD",
                "selectedHotspot": None, "predictions": {}, "observations": {}, "shares": {},
                "freshness": {"stored": False, "reason": "no runtime content uploaded yet"}}
    ga = stored.get("generated_at")
    age_seconds, stale = None, None
    if ga:
        try:
            gat = datetime.fromisoformat(ga)
            if gat.tzinfo is None:
                gat = gat.replace(tzinfo=timezone.utc)
            age_seconds = (_now() - gat).total_seconds()
            stale = age_seconds > 36 * 3600
        except Exception:
            pass
    stored["freshness"] = {"stored": True, "stored_at": stored.get("stored_at"),
                           "age_seconds": age_seconds, "stale": stale}
    return stored
