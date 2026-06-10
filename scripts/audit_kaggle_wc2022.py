#!/usr/bin/env python3
"""Kaggle WC2022 offline alignment audit.

Aligns the Kaggle international-results dataset against the Render API's 64 WC2022
finished matches to backfill / verify `final_score` + `actual_winner` and assess
derived capabilities (recent_form_5, head_to_head, upset / favorite-fail).

- If the Kaggle CSV is NOT downloaded, emits `manual_download_needed` and the
  prepared Render side (never fabricates results).
- If the CSV IS present, runs the full alignment from local data only.

Stdlib only (csv, json, urllib) — no pandas dependency.
Run:  python scripts/audit_kaggle_wc2022.py
Output: docs/data_audit/kaggle_wc2022_cross_validation.json
"""
import csv, json, os, urllib.request
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAGGLE_DIR = os.path.join(REPO, "data/external/kaggle")
RESULTS_CSV = os.path.join(KAGGLE_DIR, "results.csv")
GOALSCORERS_CSV = os.path.join(KAGGLE_DIR, "goalscorers.csv")
SHOOTOUTS_CSV = os.path.join(KAGGLE_DIR, "shootouts.csv")
# Repo-relative paths for the committed JSON (don't leak local absolute paths).
EXPECTED_REL = ["data/external/kaggle/results.csv",
                "data/external/kaggle/goalscorers.csv",
                "data/external/kaggle/shootouts.csv"]
OUT = os.path.join(REPO, "docs/data_audit/kaggle_wc2022_cross_validation.json")
API = "https://worldcup2026-api-71n6.onrender.com/api/v1"
DATASET = "martj42/international-football-results-from-1872-to-2017 (now 1872->2026)"
DATASET_URL = "https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017"
LICENSE_STATUS = ("CC0 / Public Domain per dataset page — UNCONFIRMED until operator verifies at "
                  "download; NOT for customer UI until license confirmed + Owner sign-off")

# Render team name -> canonical (martj42) name. Only 6 zh names exist in the WC2022 set.
ZH2EN = {"阿根廷": "Argentina", "法国": "France", "摩洛哥": "Morocco",
         "巴西": "Brazil", "西班牙": "Spain", "德国": "Germany"}
EN_FIX = {"USA": "United States"}  # martj42 uses 'United States'; others match directly
NORMALIZE_VERIFY = ["Iran", "South Korea"]  # confirm martj42 spelling at download

def normalize(name):
    if name in ZH2EN: return ZH2EN[name]
    if name in EN_FIX: return EN_FIX[name]
    return name

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def write(obj):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print("WROTE", OUT)

def fetch_render_wc2022():
    try:
        req = urllib.request.Request(API + "/matches", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        return None, str(e)
    out = []
    for m in data:
        if m.get("status") != "finished":
            continue
        out.append({
            "id": m["id"], "date": (m.get("kickoff_time") or "")[:10],
            "home": normalize(m["home_team"]["name"]), "away": normalize(m["away_team"]["name"]),
            "win_prob": m.get("win_prob"), "risk_level": m.get("risk_level"),
            "confidence": m.get("confidence"), "recommended_score": m.get("recommended_score"),
        })
    return out, None

def render_side_summary(render):
    teams = set()
    for m in render:
        teams.add(m["home"]); teams.add(m["away"])
    return {
        "wc2022_match_count": len(render),
        "distinct_team_count": len(teams),
        "teams_zh_to_canonical": ZH2EN,
        "english_normalizations": EN_FIX,
        "normalization_verify_at_download": NORMALIZE_VERIFY,
        "match_keys_sample": [{"id": m["id"], "date": m["date"], "home": m["home"], "away": m["away"]}
                              for m in render[:6]],
    }

def predicted_favorite(m):
    wp = m.get("win_prob") or {}
    h, d, a = wp.get("home", 0), wp.get("draw", 0), wp.get("away", 0)
    if h >= a and h >= d: return "home"
    if a >= h and a >= d: return "away"
    return "draw"

def pair(a, b):
    return tuple(sorted([a, b]))

def main():
    render, rerr = fetch_render_wc2022()
    if render is None:
        write({"source": "kaggle", "dataset": DATASET, "dataset_url": DATASET_URL,
               "license_status": LICENSE_STATUS, "checked_at": now_iso(),
               "status": "render_fetch_failed", "error": rerr,
               "expected_paths": EXPECTED_REL,
               "note": "Could not fetch Render /matches; rerun with network. No data fabricated."})
        return

    base = {"source": "kaggle", "dataset": DATASET, "dataset_url": DATASET_URL,
            "license_status": LICENSE_STATUS, "checked_at": now_iso(),
            "render_wc2022_matches": len(render), "render_side": render_side_summary(render)}

    if not os.path.exists(RESULTS_CSV):
        base.update({
            "status": "manual_download_needed",
            "expected_paths": EXPECTED_REL,
            "kaggle_wc2022_rows": None, "matched_count": None,
            "unmatched_render": None, "unmatched_kaggle": None,
            "field_coverage": {"final_score": {"status": "pending_download"},
                               "actual_winner": {"status": "pending_download"}},
            "derived_candidates": {
                "recent_form_5": "derivable offline once results.csv present (full 1872->2026 history)",
                "head_to_head": "derivable offline once results.csv present (full history)",
                "upset_cases": "derivable once final_score/actual_winner present (vs predicted favorite)",
                "favorite_failed_cases": "derivable once final_score present",
            },
            "note": "Render side prepared (64 matches + normalizer). Awaiting operator Kaggle download. No data fabricated.",
        })
        write(base)
        print("status=manual_download_needed (no CSV at %s)" % RESULTS_CSV)
        return

    # ---- full alignment (runs only when the operator has placed the CSV) ----
    wc = []
    with open(RESULTS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("tournament") == "FIFA World Cup" and row.get("date", "")[:4] == "2022":
                wc.append(row)

    # Optional penalty-shootout winners (KO matches level after 90/120') -> accurate actual_winner.
    shootout = {}
    if os.path.exists(SHOOTOUTS_CSV):
        with open(SHOOTOUTS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("date", "")[:4] == "2022":
                    shootout[pair(normalize(row["home_team"]), normalize(row["away_team"]))] = normalize(row["winner"])

    kindex = {}
    for row in wc:
        kindex.setdefault(pair(normalize(row["home_team"]), normalize(row["away_team"])), []).append(row)

    matched, unmatched_render, used = [], [], set()
    for m in render:
        cands = kindex.get(pair(m["home"], m["away"]), [])
        pick = None
        for row in cands:
            if id(row) in used:
                continue
            if row["date"] == m["date"]:
                pick = row; break
            pick = pick or row
        if pick is None:
            unmatched_render.append({"id": m["id"], "date": m["date"], "home": m["home"], "away": m["away"]})
            continue
        used.add(id(pick))
        hs, as_ = int(pick["home_score"]), int(pick["away_score"])
        if normalize(pick["home_team"]) == m["home"]:
            rh, ra = hs, as_
        else:
            rh, ra = as_, hs
        winner = m["home"] if rh > ra else (m["away"] if ra > rh else "draw")
        decided = "regulation"
        if winner == "draw":
            sw = shootout.get(pair(m["home"], m["away"]))
            if sw:
                winner, decided = sw, "penalties"
        fav = predicted_favorite(m)
        fav_team = {"home": m["home"], "away": m["away"], "draw": "draw"}[fav]
        is_upset = fav != "draw" and winner not in ("draw", fav_team)
        matched.append({"id": m["id"], "date": m["date"], "home": m["home"], "away": m["away"],
                        "final_score": "%d-%d" % (rh, ra), "actual_winner": winner, "decided_by": decided,
                        "predicted_favorite": fav_team, "favorite_failed": is_upset})

    unmatched_kaggle = [{"date": r["date"], "home": normalize(r["home_team"]), "away": normalize(r["away_team"])}
                        for r in wc if id(r) not in used]
    upsets = [x for x in matched if x["favorite_failed"]]
    fs = sum(1 for x in matched if x["final_score"])
    base.update({
        "status": "alignment_complete",
        "kaggle_wc2022_rows": len(wc), "matched_count": len(matched),
        "unmatched_render": unmatched_render, "unmatched_kaggle": unmatched_kaggle,
        "field_coverage": {"final_score": {"present": fs, "missing": len(render) - fs},
                           "actual_winner": {"present": len(matched), "missing": len(render) - len(matched)}},
        "upset_cases_count": len(upsets), "upset_cases": upsets[:20],
        "derived_candidates": {
            "recent_form_5": "derivable (compute from full results.csv history)",
            "head_to_head": "derivable (full history)",
            "upset_cases": "computed: %d favorite-failed of %d matched" % (len(upsets), len(matched)),
            "favorite_failed_cases": "%d cases" % len(upsets),
        },
        "note": "Alignment from LOCAL Kaggle CSV only. Internal validation; customer UI needs license confirmation + Owner sign-off.",
    })
    write(base)
    print("status=alignment_complete matched=%d/%d upsets=%d" % (len(matched), len(render), len(upsets)))

if __name__ == "__main__":
    main()
