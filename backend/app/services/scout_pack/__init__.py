"""MVP-2 Pre-match Scout Pack — internal ingestion + contract (server-side only).

This package turns real API-FOOTBALL Level-2 responses into a redacted,
provenance-tagged internal Scout Pack for operator review. No fabrication:
a field is `available` only when a real source returned it; missing fields
render an honest, localized "source required". Never customer-facing yet.
"""
from app.services.scout_pack.contract import (  # noqa: F401
    SCOUT_PACK_SCHEMA_VERSION,
    SOURCE_API_FOOTBALL,
    SECTION_KEYS,
    evidence_field,
    loc,
)
from app.services.scout_pack.builder import build_scout_pack  # noqa: F401
