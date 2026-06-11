#!/usr/bin/env python3
"""
MVP-2 Track A — file-based artifact registry + operator review queue (A5).

Library used by scripts/mvp2_ops.py (and the A3/A4 builders); also runnable:
  python3 scripts/mvp2_ops_queue.py --selftest      # state machine + refusal rules in a tmp dir

Design: docs/MVP2_TRACK_A_AUTOMATED_OPERATION_DESIGN.md §4-§5 (Owner A-GO-1).
- States: generated / guard_passed / needs_review / approved / sent / expired
          (+ terminal hygiene: rejected / superseded)
- Items live in docs/data_audit/mvp2_review_queue/items/{item_id}.json (truth);
  queue.json is a regenerated index. git history = audit log.
- HARD RULES enforced here (not by convention):
  * approve refuses mock items, expired items, sha256-mismatched artifacts
    (any hand edit ⇒ re-generate + re-guard; Owner: 不得人工改写判断文案)
  * needs_review -> approved requires a --note
  * mark-sent requires channel/group/screenshot and only from approved
  * NOTHING here sends anything — "sent" records a human act after the fact
- Regeneration never mutates history: new item + old item -> superseded.
"""
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE_DIR = ROOT / "docs" / "data_audit" / "mvp2_review_queue"
REGISTRY_DIR = ROOT / "docs" / "data_audit" / "mvp2_ops_registry"
RUNS_DIR = ROOT / "docs" / "data_audit" / "mvp2_ops_runs"

OPEN_STATES = ("generated", "guard_passed", "needs_review", "approved")
TERMINAL_STATES = ("sent", "expired", "rejected", "superseded")
ALL_STATES = OPEN_STATES + TERMINAL_STATES


# ── small shared utils (registry + builders import these) ────────────────────
def now_utc():
    return datetime.now(timezone.utc)


def iso(dt=None):
    return (dt or now_utc()).isoformat(timespec="seconds")


def new_run_id(job):
    return "r%s-%s" % (now_utc().strftime("%Y%m%dT%H%MZ"), job)


def sha256_file(path):
    p = pathlib.Path(path)
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_obj(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def read_json(path, default=None):
    p = pathlib.Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(path, obj):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ── per-fixture manifest (registry) ──────────────────────────────────────────
def manifest_path(fixture_id, base=None):
    return (base or REGISTRY_DIR) / ("%s.manifest.json" % fixture_id)


def load_manifest(fixture_id, base=None):
    return read_json(manifest_path(fixture_id, base), default={
        "fixture_id": str(fixture_id), "match": None, "kickoff_utc": None,
        "key_match": None, "key_reasons": [], "stages": {},
        "lineups_released": False, "quota_ledger_day": {},
    })


def save_manifest(m, base=None):
    m["updated_at"] = iso()
    write_json(manifest_path(m["fixture_id"], base), m)


def record_stage(fixture_id, stage, payload, lang=None, base=None):
    """Record a stage result in the per-fixture manifest (lang-keyed when given)."""
    m = load_manifest(fixture_id, base)
    if lang:
        m["stages"].setdefault(stage, {})[lang] = payload
    else:
        m["stages"][stage] = payload
    save_manifest(m, base)
    return m


def bump_quota(fixture_id, n, daily_budget=100, base=None):
    m = load_manifest(fixture_id, base)
    day = now_utc().strftime("%Y-%m-%d")
    q = m.get("quota_ledger_day") or {}
    if q.get("date") != day:
        q = {"date": day, "requests": 0, "daily_budget": daily_budget}
    q["requests"] = int(q.get("requests", 0)) + n
    m["quota_ledger_day"] = q
    save_manifest(m, base)
    if q["requests"] >= q["daily_budget"]:
        return "blocked_quota"
    if q["requests"] >= 0.7 * q["daily_budget"]:
        return "warn"
    return "ok"


# ── run manifest ─────────────────────────────────────────────────────────────
class RunManifest:
    """Every command writes one — failures write a manifest, never silently fail."""

    def __init__(self, job, fixtures=None, base=None):
        self.base = base or RUNS_DIR
        self.run_id = new_run_id(job)
        self.doc = {"run_id": self.run_id, "job": job, "fixtures": [str(f) for f in (fixtures or [])],
                    "started_at": iso(), "finished_at": None, "git_rev": _git_rev(),
                    "steps": [], "api_request_ledger": {"count": 0, "by_endpoint": {}},
                    "llm_calls": {}, "guard_summary": None, "status": "running"}
        self.flush()

    @property
    def dir(self):
        return self.base / self.run_id

    def flush(self):
        write_json(self.dir / "run.json", self.doc)

    def step(self, name, status, detail=None, artifact_paths=None):
        self.doc["steps"].append({"name": name, "status": status, "at": iso(),
                                  "detail": detail, "artifact_paths": artifact_paths or []})
        self.flush()

    def api(self, endpoint, n=1):
        led = self.doc["api_request_ledger"]
        led["count"] += n
        led["by_endpoint"][endpoint] = led["by_endpoint"].get(endpoint, 0) + n
        self.flush()

    def finish(self, status, guard_summary=None):
        self.doc["status"] = status
        self.doc["guard_summary"] = guard_summary
        self.doc["finished_at"] = iso()
        self.flush()
        return self.doc


def _git_rev():
    try:
        import subprocess
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception:
        return None


# ── queue items ──────────────────────────────────────────────────────────────
def _items_dir(base=None):
    return (base or QUEUE_DIR) / "items"


def item_path(item_id, base=None):
    return _items_dir(base) / ("%s.json" % item_id)


def load_item(item_id, base=None):
    it = read_json(item_path(item_id, base))
    if it is None:
        raise SystemExit("queue: no such item: %s" % item_id)
    return it


def save_item(it, base=None):
    write_json(item_path(it["item_id"], base), it)
    rebuild_index(base)


def list_items(base=None, fixture=None, status=None):
    out = []
    d = _items_dir(base)
    if d.exists():
        for p in sorted(d.glob("*.json")):
            it = read_json(p)
            if fixture and it.get("fixture_id") != str(fixture):
                continue
            if status and it.get("status") != status:
                continue
            out.append(it)
    return out


def rebuild_index(base=None):
    idx = {it["item_id"]: {"status": it["status"], "fixture_id": it["fixture_id"],
                           "surface": it["surface"], "language": it["language"],
                           "expires_at": it.get("expires_at")}
           for it in list_items(base)}
    write_json((base or QUEUE_DIR) / "queue.json", {"generated_at": iso(), "items": idx})


def _transition(it, new_status, by, note=None):
    it["status"] = new_status
    it.setdefault("status_history", []).append(
        {"status": new_status, "at": iso(), "by": by, **({"note": note} if note else {})})
    return it


def _safe_id(s):
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(s))


def register(artifact_path, *, fixture_id, job, surface, language, provider, run_id,
             guard_errors, guard_report_path=None, inputs_hash=None, expires_at=None, base=None):
    """Register an artifact as a queue item (generated -> guard_passed|needs_review).
    Supersedes any open item for the same (fixture, surface, language)."""
    artifact_path = pathlib.Path(artifact_path)
    if not artifact_path.exists():
        raise SystemExit("queue.register: artifact missing: %s" % artifact_path)
    item_id = ".".join(_safe_id(x) for x in (fixture_id, surface, language, provider, run_id))
    it = {
        "item_id": item_id, "fixture_id": str(fixture_id), "job": job, "surface": surface,
        "language": language, "provider": provider, "run_id": run_id,
        "artifact_path": str(artifact_path.relative_to(ROOT)) if str(artifact_path).startswith(str(ROOT)) else str(artifact_path),
        "artifact_sha256": sha256_file(artifact_path),
        "guard_report_path": guard_report_path, "inputs_hash": inputs_hash,
        "status": "generated",
        "status_history": [{"status": "generated", "at": iso(), "by": "pipeline"}],
        "expires_at": expires_at, "approved_by": None, "review_note": None,
        "superseded_by": None, "sent_record": None,
    }
    if guard_errors:
        _transition(it, "needs_review", "guard", note="; ".join(guard_errors[:6]))
    else:
        _transition(it, "guard_passed", "guard")
    # supersede older open items for the same slot
    for old in list_items(base, fixture=fixture_id):
        if (old["surface"], old["language"]) == (surface, language) \
                and old["item_id"] != item_id and old["status"] in OPEN_STATES:
            old["superseded_by"] = item_id
            _transition(old, "superseded", "pipeline", note="superseded by %s" % item_id)
            write_json(item_path(old["item_id"], base), old)
    save_item(it, base)
    return it


def _expired(it):
    exp = it.get("expires_at")
    return bool(exp) and iso() >= exp


def sweep(base=None, by="sweep"):
    """Expire any open pre-match item past its expires_at. Run before every queue command."""
    expired = []
    for it in list_items(base):
        if it["status"] in OPEN_STATES and _expired(it):
            _transition(it, "expired", by, note="kickoff passed")
            write_json(item_path(it["item_id"], base), it)
            expired.append(it["item_id"])
    rebuild_index(base)
    return expired


def approve(item_id, by, note=None, base=None):
    sweep(base)
    it = load_item(item_id, base)
    if it["provider"] == "mock":
        raise SystemExit("queue.approve REFUSED: mock artifacts are never approvable (%s)" % item_id)
    if it["status"] == "expired" or _expired(it):
        raise SystemExit("queue.approve REFUSED: item expired at %s (pre-match copy dies at kickoff)" % it.get("expires_at"))
    if it["status"] not in ("guard_passed", "needs_review"):
        raise SystemExit("queue.approve REFUSED: status %s is not reviewable" % it["status"])
    if it["status"] == "needs_review" and not note:
        raise SystemExit("queue.approve REFUSED: needs_review -> approved requires --note (override reason)")
    current = sha256_file(ROOT / it["artifact_path"])
    if current != it["artifact_sha256"]:
        raise SystemExit("queue.approve REFUSED: artifact sha256 mismatch — file was edited after "
                         "registration. Regenerate + re-guard (不得人工改写判断文案). item=%s" % item_id)
    it["approved_by"] = by
    it["review_note"] = note
    _transition(it, "approved", by, note)
    save_item(it, base)
    return it


def reject(item_id, by, note, base=None):
    if not note:
        raise SystemExit("queue.reject requires --note")
    it = load_item(item_id, base)
    if it["status"] in TERMINAL_STATES:
        raise SystemExit("queue.reject REFUSED: terminal status %s" % it["status"])
    it["review_note"] = note
    _transition(it, "rejected", by, note)
    save_item(it, base)
    return it


def mark_sent(item_id, by, channel, group, screenshot, base=None):
    """Records a HUMAN send that already happened. This tool never sends anything."""
    sweep(base)
    if not (channel and group and screenshot):
        raise SystemExit("queue.mark-sent requires --channel --group --screenshot")
    it = load_item(item_id, base)
    if it["status"] != "approved":
        raise SystemExit("queue.mark-sent REFUSED: only approved items can be marked sent (status=%s)" % it["status"])
    if _expired(it):
        raise SystemExit("queue.mark-sent REFUSED: item expired — do not record post-kickoff sends; report to Owner")
    it["sent_record"] = {"at": iso(), "by": by, "channel": channel, "group": group, "screenshot_path": screenshot}
    _transition(it, "sent", by)
    save_item(it, base)
    return it


# ── selftest ─────────────────────────────────────────────────────────────────
def _selftest():
    import tempfile
    ok = []

    def check(name, fn, expect_fail=False):
        try:
            fn()
            ok.append((name, not expect_fail))
        except SystemExit:
            ok.append((name, expect_fail))

    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        art = base / "a.json"
        art.write_text('{"x": 1}\n', encoding="utf-8")
        future = "2999-01-01T00:00:00+00:00"
        past = "2000-01-01T00:00:00+00:00"

        it = register(art, fixture_id="900", job="A2_prematch", surface="trial_prediction",
                      language="zh-CN", provider="deepseek", run_id="rTESTZ-prematch",
                      guard_errors=[], expires_at=future, base=base)
        ok.append(("register -> guard_passed", it["status"] == "guard_passed"))
        check("approve guard_passed OK", lambda: approve(it["item_id"], "tester", base=base))
        check("mark-sent w/o screenshot refused",
              lambda: mark_sent(it["item_id"], "tester", "telegram", "g", "", base=base), expect_fail=True)
        check("mark-sent OK", lambda: mark_sent(it["item_id"], "tester", "telegram", "g", "shot.png", base=base))

        # sha mismatch refusal
        it2 = register(art, fixture_id="900", job="A2_prematch", surface="trial_prediction",
                       language="vi-VN", provider="deepseek", run_id="rTESTZ-prematch",
                       guard_errors=[], expires_at=future, base=base)
        art.write_text('{"x": 2}\n', encoding="utf-8")  # tamper
        check("approve sha-mismatch refused",
              lambda: approve(it2["item_id"], "tester", base=base), expect_fail=True)

        # mock refusal
        it3 = register(art, fixture_id="900", job="A2_prematch", surface="trial_prediction",
                       language="my-MM", provider="mock", run_id="rTESTZ-prematch",
                       guard_errors=[], expires_at=future, base=base)
        check("approve mock refused", lambda: approve(it3["item_id"], "tester", base=base), expect_fail=True)

        # needs_review requires note
        it4 = register(art, fixture_id="901", job="A2_prematch", surface="trial_prediction",
                       language="zh-CN", provider="deepseek", run_id="rTESTZ-prematch",
                       guard_errors=["synthetic guard error"], expires_at=future, base=base)
        ok.append(("register w/ errors -> needs_review", it4["status"] == "needs_review"))
        check("needs_review approve w/o note refused",
              lambda: approve(it4["item_id"], "tester", base=base), expect_fail=True)
        check("needs_review approve w/ note OK",
              lambda: approve(it4["item_id"], "tester", note="override: reviewed", base=base))

        # expiry sweep + expired approve refusal
        it5 = register(art, fixture_id="902", job="A2_prematch", surface="trial_prediction",
                       language="zh-CN", provider="deepseek", run_id="rTESTZ-prematch",
                       guard_errors=[], expires_at=past, base=base)
        swept = sweep(base)
        ok.append(("sweep expires past-kickoff item", it5["item_id"] in swept))
        check("approve expired refused", lambda: approve(it5["item_id"], "tester", base=base), expect_fail=True)

        # supersede on re-register
        it6 = register(art, fixture_id="901", job="A2_prematch", surface="trial_prediction",
                       language="zh-CN", provider="deepseek", run_id="rTEST2Z-prematch",
                       guard_errors=[], expires_at=future, base=base)
        old = load_item(it4["item_id"], base)
        ok.append(("re-register supersedes old open item",
                   old["status"] == "superseded" and old["superseded_by"] == it6["item_id"]))

    failed = [n for n, good in ok if not good]
    for n, good in ok:
        print("%s  %s" % ("PASS" if good else "FAIL", n))
    print("\nQUEUE SELFTEST %s (%d/%d)" % ("PASS" if not failed else "FAIL", len(ok) - len(failed), len(ok)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    print(__doc__)
