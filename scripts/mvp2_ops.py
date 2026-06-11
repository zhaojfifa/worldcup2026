#!/usr/bin/env python3
"""
MVP-2 Track A — P0 local operations orchestrator (design §1-§6; Owner A-GO-1).

ONE operator-triggered entry point that WRAPS the existing pipeline scripts —
it rewrites nothing, generates no narrative itself, and NEVER sends anything.
Every command writes a run manifest (failures included); every artifact is
registered (path / sha256 / run_id / language / provider / guard status /
expires_at for pre-match surfaces); every command is safe to re-run
(regeneration supersedes, never mutates queue history).

  scan                                  A1 daily upcoming-match scan
  prematch  --fixture ID                A2 chain (verify -> pack -> frame -> narratives
            [--register-existing]          x3 langs -> rescore models x3 -> guard ->
            [--langs a,b] [--providers]    send-kit -> queue registration)
  watch     --fixture ID [--once]       T-90 lineup watch (poll; alert; auto-run A3;
            [--interval 300] [--no-auto]   operator stays in the loop — nothing sends)
  rescore   --fixture ID [--langs]      A3 rescore diff + guarded LLM update
  recap     --fixture ID [--langs]      A4 real-recap frame + guarded narratives
  bundle    --fixture ID                copy guard-passed artifacts into the frontend
                                        bundle dirs (refuses expired/mock/guard-fail)
  queue     list|show|approve|reject|mark-sent|sweep ...
  status    --fixture ID                per-fixture manifest + queue summary

Hard lines (enforced, not advisory): no auto-send · pre-match generation refused
after T-12 · pre-match artifacts expire at kickoff · mock never registered as
approvable · my-MM mock never exists · keys never printed.
"""
import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DOCS = ROOT / "docs" / "data_audit"
SEND_KITS = DOCS / "mvp2_send_kits"
FRAMES = DOCS / "mvp2_trial_prediction_frames"
NARR = DOCS / "mvp2_trial_prediction_narratives"
RESCORE_MODELS = DOCS / "mvp2_rescore_models"
PROOF = DOCS / "mvp2_product_proof_narratives"
RESCORE_RUNS = DOCS / "mvp2_rescore_runs"
FE_NARR = ROOT / "frontend" / "src" / "data" / "productNarratives"
FE_RESCORE = ROOT / "frontend" / "src" / "data" / "rescoreModels"
LANGS = ("zh-CN", "vi-VN", "my-MM")
# fixtures whose JSONs are statically imported in the frontend today (new fixtures
# need the documented engineer import step — see design §2 decision 2 / P1 glob)
BUNDLED_IMPORT_IDS = {"855737", "979139", "2026_brazil_argentina", "1489369", "1489371"}
ABORT_BEFORE_KICKOFF_MIN = 12


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


Q = _load("opsq", SCRIPTS / "mvp2_ops_queue.py")
GUARDMOD = _load("guard", SCRIPTS / "check_mvp2_product_narrative_guard.py")


def _now():
    return datetime.now(timezone.utc)


def _kickoff(fid):
    m = Q.load_manifest(fid)
    if m.get("kickoff_utc"):
        return m["kickoff_utc"]
    fr = Q.read_json(FRAMES / ("%s.json" % fid))
    return (fr or {}).get("fixture", {}).get("kickoff")


def _minutes_to_kickoff(fid):
    ko = _kickoff(fid)
    if not ko:
        return None, None
    dt = datetime.fromisoformat(ko)
    return (dt - _now()).total_seconds() / 60.0, ko


def _run_script(run, name, script, args, cwd=None):
    """Wrapper-first: call an existing pipeline script as a subprocess, record the step."""
    cmd = [sys.executable, str(script)] + [str(a) for a in args]
    r = subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True, timeout=1800)
    status = "ok" if r.returncode == 0 else "failed"
    tail = (r.stdout or r.stderr or "").strip().splitlines()[-3:]
    run.step(name, status, detail=" | ".join(tail)[:400])
    return r.returncode == 0


_RG = None
# engineering meta stamped AFTER the generator's own final check — strip before re-validation
# (e.g. model="deepseek-chat" would false-positive the de-model scan)
_RESCORE_META = ("llm_provider", "model", "voice", "generated_at", "product_surface", "guard_clean")


def _check_artifact(p):
    """Dispatch to the right gate per surface — reuse, never duplicate (design §8):
    trial_rescore -> rescore generator's own check(); trial_rescore_update -> new guard
    checker; everything else -> narrative-contract check()."""
    global _RG
    obj = Q.read_json(p)
    surface = (obj or {}).get("product_surface")
    if surface == "trial_rescore":
        if _RG is None:
            _RG = _load("rg", SCRIPTS / "mvp2_generate_rescore_models.py")
        body = {k: v for k, v in obj.items() if k not in _RESCORE_META}
        return _RG.check(body, obj.get("language"))
    if surface == "trial_rescore_update":
        return GUARDMOD.check_rescore_update_obj(obj, p.name)
    return GUARDMOD.check(p)


def _guard_report(run, paths):
    """Structured guard report over artifact paths (per-surface dispatch)."""
    report = {}
    for p in paths:
        p = pathlib.Path(p)
        report[str(p.relative_to(ROOT))] = _check_artifact(p) if p.exists() else ["artifact missing"]
    rp = run.dir / "guard_report.json"
    Q.write_json(rp, report)
    n_fail = sum(1 for v in report.values() if v)
    run.step("guard", "ok" if n_fail == 0 else "failed",
             detail="%d/%d artifacts clean" % (len(report) - n_fail, len(report)),
             artifact_paths=[str(rp.relative_to(ROOT))])
    return report, rp


# ── A1 ───────────────────────────────────────────────────────────────────────
def cmd_scan(args):
    run = Q.RunManifest("scan")
    ds = _load("ds", SCRIPTS / "mvp2_daily_scan.py")
    out, doc = ds.scan(args.date, run=run)
    run.step("scan", "ok", detail=str(out.relative_to(ROOT)),
             artifact_paths=[str(out.relative_to(ROOT))])
    run.finish("partial" if doc["degraded"] else "ok")
    keys = [w for w in doc["fixtures_today"] + doc["fixtures_next_day"] if w["key_match"]]
    print("scan %s: today=%d next=%d key=%d degraded=%s -> %s" % (
        doc["date"], len(doc["fixtures_today"]), len(doc["fixtures_next_day"]),
        len(keys), doc["degraded"], out.relative_to(ROOT)))
    for w in keys:
        print("  KEY %s %s  %s" % (w["fixture_id"], w["match"], ",".join(w["key_reasons"])))
        for a in w["actions_needed"]:
            print("    -> %s" % a)
    return 0


# ── A2 ───────────────────────────────────────────────────────────────────────
def _send_kit_prematch(fid, guard_report):
    """Assemble the operator send-kit FROM GUARD-PASSED LLM FIELDS ONLY.
    Engineering writes zero narrative — it quotes artifacts verbatim."""
    ko = _kickoff(fid) or "?"
    lines = ["# Send-kit · fixture %s · PRE-MATCH (auto-assembled, quotes LLM artifacts verbatim)" % fid,
             "",
             "> expires_at(kickoff): **%s** — 开球后本 kit 全部作废。" % ko,
             "> 群链接一律 [群链接由运营填写]；文案不得人工改写；发送前过 GO/NO-GO 清单。",
             ""]
    for lang in LANGS:
        npath = NARR / ("%s.%s.deepseek.json" % (fid, lang))
        rpath = RESCORE_MODELS / ("%s.%s.deepseek.json" % (fid, lang))
        nrel = str(npath.relative_to(ROOT)) if npath.exists() else None
        if not nrel or guard_report.get(nrel):
            lines += ["## %s — SKIPPED (no guard-passed narrative)" % lang, ""]
            continue
        n = Q.read_json(npath)
        lines += ["## %s（persona 原文引用 · %s）" % (lang, nrel),
                  "", "**群消息（operator_copy）**", "```text", n.get("operator_copy", ""),
                  "👉 [群链接由运营填写]", "```",
                  "**短帖（social_post）**", "```text", n.get("social_post", ""), "```",
                  "**入群钩子（group_join_copy）**", "```text", n.get("group_join_copy", ""), "```"]
        if rpath.exists() and not guard_report.get(str(rpath.relative_to(ROOT)), ["?"]):
            r = Q.read_json(rpath)
            lines += ["**30 分钟提醒（reminder_message）**", "```text", r.get("reminder_message", ""), "```",
                      "**重算 teaser（public_teaser）**", "```text", r.get("public_teaser", ""), "```"]
        lines += [""]
    out = SEND_KITS / ("%s.prematch.md" % fid)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def cmd_prematch(args):
    fid = args.fixture
    langs = args.langs.split(",") if args.langs else list(LANGS)
    run = Q.RunManifest("prematch", [fid])
    mins, ko = _minutes_to_kickoff(fid)
    if mins is not None and mins <= ABORT_BEFORE_KICKOFF_MIN:
        run.finish("aborted_window")
        print("REFUSED: %.0f min to kickoff (<= T-%d) — no new pre-match generation. (run %s)"
              % (mins, ABORT_BEFORE_KICKOFF_MIN, run.run_id))
        return 2

    if not args.register_existing:
        # verify rewrites the verification file for the GIVEN candidates — always pass the
        # union of known registry fixtures so earlier entries are never clobbered
        known = sorted({p.stem.split(".")[0] for p in (DOCS / "mvp2_ops_registry").glob("*.manifest.json")} | {str(fid)})
        ok = _run_script(run, "verify", SCRIPTS / "mvp2_verify_june11_fixtures.py", known)
        ok = ok and _run_script(run, "scout_pack", ROOT / "backend" / "scripts" / "mvp2_ingest_scout_pack.py", [fid])
        ok = ok and _run_script(run, "frame", SCRIPTS / "mvp2_build_trial_prediction_frame.py", [fid])
        for lang in langs:
            ok = _run_script(run, "narrative.%s" % lang,
                             SCRIPTS / "mvp2_generate_trial_prediction_narratives.py",
                             [args.providers, fid, lang]) and ok
            ok = _run_script(run, "rescore_model.%s" % lang,
                             SCRIPTS / "mvp2_generate_rescore_models.py",
                             [args.providers, fid, lang]) and ok
        if not ok:
            print("prematch: one or more steps failed — see run manifest %s" % run.run_id)
    else:
        run.step("register_existing", "ok", detail="skipping generation; registering existing artifacts")

    arts = []
    for lang in langs:
        for base in (NARR, RESCORE_MODELS):
            p = base / ("%s.%s.deepseek.json" % (fid, lang))
            if p.exists():
                arts.append(p)
    if not arts:
        run.finish("failed")
        print("prematch: no artifacts found for %s — nothing to register (run %s)" % (fid, run.run_id))
        return 1
    report, rp = _guard_report(run, arts)

    ko = _kickoff(fid)
    frame_path = FRAMES / ("%s.json" % fid)
    inputs_hash = Q.sha256_file(frame_path) if frame_path.exists() else None
    registered = []
    for p in arts:
        rel = str(p.relative_to(ROOT))
        obj = Q.read_json(p)
        surface = "trial_prediction" if p.parent == NARR else "trial_rescore"
        it = Q.register(p, fixture_id=fid, job="A2_prematch", surface=surface,
                        language=obj.get("language", "?"), provider=obj.get("llm_provider", "?"),
                        run_id=run.run_id, guard_errors=report.get(rel, []),
                        guard_report_path=str(rp.relative_to(ROOT)),
                        inputs_hash=inputs_hash, expires_at=ko)
        registered.append((it["item_id"], it["status"]))
        Q.record_stage(fid, "prematch_narratives" if surface == "trial_prediction" else "rescore_model",
                       {"status": it["status"], "artifact": rel, "queue_item": it["item_id"],
                        "run_id": run.run_id, "expires_at": ko}, lang=obj.get("language"))
    kit = _send_kit_prematch(fid, report)
    run.step("send_kit", "ok", artifact_paths=[str(kit.relative_to(ROOT))])
    Q.bump_quota(fid, run.doc["api_request_ledger"]["count"])
    n_fail = sum(1 for v in report.values() if v)
    run.finish("ok" if n_fail == 0 else "partial",
               guard_summary="%d/%d clean" % (len(report) - n_fail, len(report)))
    print("prematch %s: %d artifacts registered (guard %d/%d clean) · send-kit %s · run %s"
          % (fid, len(registered), len(report) - n_fail, len(report), kit.relative_to(ROOT), run.run_id))
    for iid, st in registered:
        print("  %-12s %s" % (st, iid))
    return 0 if n_fail == 0 else 1


# ── A3 ───────────────────────────────────────────────────────────────────────
def _send_kit_rescore(fid, results, run_id):
    lines = ["# Send-kit · fixture %s · 30-MIN RESCORE UPDATE (run %s)" % (fid, run_id),
             "", "> 仅在运营评审 approve 后发送；开球后作废。", ""]
    for r in results:
        if r.get("status") != "guard_passed":
            lines += ["## %s — %s" % (r.get("language"), r.get("status")), ""]
            continue
        obj = Q.read_json(ROOT / r["artifact"])
        lines += ["## %s（%s）" % (r["language"], r["artifact"]),
                  "", "**群内修正消息（group_update_message）**", "```text",
                  obj.get("group_update_message", ""), "```", ""]
    out = SEND_KITS / ("%s.rescore_update.md" % fid)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def cmd_rescore(args):
    fid = args.fixture
    langs = args.langs.split(",") if args.langs else list(LANGS)
    run = Q.RunManifest("rescore", [fid])
    mins, ko = _minutes_to_kickoff(fid)
    if mins is not None and mins <= ABORT_BEFORE_KICKOFF_MIN:
        run.finish("aborted_window")
        print("REFUSED: %.0f min to kickoff (<= T-%d) — template-only fallback from here. (run %s)"
              % (mins, ABORT_BEFORE_KICKOFF_MIN, run.run_id))
        return 2
    rd = _load("rd", SCRIPTS / "mvp2_build_rescore_diff.py")
    res = rd.build_and_generate(fid, langs, run=run)
    Q.bump_quota(fid, run.doc["api_request_ledger"]["count"])
    if res["status"] != "ok":
        run.step("rescore_diff", "blocked", detail=res.get("reason") or res["status"])
        run.finish("blocked_by_time_or_data" if "blocked" in res["status"] else res["status"])
        print("rescore %s: %s (%s) · run %s" % (fid, res["status"], res.get("reason", "-"), run.run_id))
        return 2
    m = Q.load_manifest(fid)
    m["lineups_released"] = True
    Q.save_manifest(m)
    registered = []
    for r in res["results"]:
        if r.get("status") != "guard_passed":
            run.step("rescore_update.%s" % r.get("language"), r.get("status", "failed"),
                     detail="; ".join(r.get("errors", []))[:300])
            Q.record_stage(fid, "rescore_update", {"status": r.get("status"), "run_id": run.run_id},
                           lang=r.get("language"))
            continue
        p = ROOT / r["artifact"]
        it = Q.register(p, fixture_id=fid, job="A3_rescore", surface="trial_rescore_update",
                        language=r["language"], provider="deepseek", run_id=res["run_id"],
                        guard_errors=[], inputs_hash=Q.sha256_obj(res["skeleton_teams"]),
                        expires_at=_kickoff(fid))
        registered.append(it["item_id"])
        Q.record_stage(fid, "rescore_update", {"status": "guard_passed", "artifact": r["artifact"],
                                               "queue_item": it["item_id"], "run_id": res["run_id"]},
                       lang=r["language"])
    kit = _send_kit_rescore(fid, res["results"], res["run_id"])
    run.step("send_kit", "ok", artifact_paths=[str(kit.relative_to(ROOT))])
    ok_n = len(registered)
    run.finish("ok" if ok_n == len(langs) else ("partial" if ok_n else "failed"))
    print("rescore %s: %d/%d langs guard-passed · kit %s · run %s"
          % (fid, ok_n, len(langs), kit.relative_to(ROOT), run.run_id))
    return 0 if ok_n else 1


def cmd_watch(args):
    fid = args.fixture
    rd = _load("rd", SCRIPTS / "mvp2_build_rescore_diff.py")
    run = Q.RunManifest("watch", [fid])
    interval = max(60, args.interval)
    while True:
        mins, ko = _minutes_to_kickoff(fid)
        teams, info = rd.fetch_facts(fid, run=run)
        ts = _now().strftime("%H:%M:%SZ")
        if teams:
            run.step("probe", "lineups_posted", detail="teams=%d" % len(teams))
            m = Q.load_manifest(fid)
            m["lineups_released"] = True
            Q.save_manifest(m)
            print("\a[%s] LINEUPS POSTED for %s (%s) — T%+.0fmin" % (ts, fid, info.get("status_short"), -(mins or 0)))
            _notify("MVP2 watch", "Lineups posted for %s — rescore starting" % fid)
            run.finish("ok")
            if args.no_auto:
                print("(--no-auto: run `mvp2_ops.py rescore --fixture %s` now)" % fid)
                return 0
            ns = argparse.Namespace(fixture=fid, langs=args.langs)
            return cmd_rescore(ns)
        state = "NS lineups=0"
        print("[%s] %s %s · kickoff %s · T-%.0fmin" % (ts, fid, state, ko, mins if mins else -1))
        run.step("probe", "no_lineups", detail="T-%.0fmin" % (mins or -1))
        if mins is not None and mins <= ABORT_BEFORE_KICKOFF_MIN:
            run.finish("aborted_window")
            print("watch: T-%d reached without lineups — template-only fallback (GO/NO-GO §2)." % ABORT_BEFORE_KICKOFF_MIN)
            return 2
        if args.once:
            run.finish("ok")
            return 0
        time.sleep(interval)


def _notify(title, body):
    try:
        subprocess.run(["osascript", "-e",
                        'display notification "%s" with title "%s"' % (body.replace('"', ''), title.replace('"', ''))],
                       capture_output=True, timeout=5)
    except Exception:
        pass


# ── A4 ───────────────────────────────────────────────────────────────────────
def cmd_recap(args):
    fid = args.fixture
    langs = args.langs.split(",") if args.langs else list(LANGS)
    run = Q.RunManifest("recap", [fid])
    rr = _load("rr", SCRIPTS / "mvp2_build_recap_frame_real.py")
    res = rr.build(fid, run=run)
    Q.bump_quota(fid, run.doc["api_request_ledger"]["count"])
    if res["status"] != "ok":
        run.step("real_recap_frame", "blocked", detail=res.get("reason", ""))
        run.finish("blocked_by_time_or_data")
        print("recap %s: blocked_by_time_or_data — %s · run %s" % (fid, res.get("reason"), run.run_id))
        return 2
    run.step("real_recap_frame", "ok", artifact_paths=[res["artifact"]])
    arts = []
    if not args.skip_generate:
        for lang in langs:
            _run_script(run, "recap_narrative.%s" % lang,
                        SCRIPTS / "mvp2_generate_product_proof_narratives.py",
                        ["deepseek", fid, lang])
            p = PROOF / ("%s.%s.deepseek.json" % (fid, lang))
            if p.exists():
                arts.append(p)
    if arts:
        report, rp = _guard_report(run, arts)
        for p in arts:
            rel = str(p.relative_to(ROOT))
            obj = Q.read_json(p)
            if obj.get("mode") != "real_recap":
                run.step("register.%s" % obj.get("language"), "skipped",
                         detail="mode=%s (not real_recap)" % obj.get("mode"))
                continue
            it = Q.register(p, fixture_id=fid, job="A4_recap", surface="recap",
                            language=obj.get("language", "?"), provider=obj.get("llm_provider", "?"),
                            run_id=run.run_id, guard_errors=report.get(rel, []),
                            guard_report_path=str(rp.relative_to(ROOT)),
                            inputs_hash=Q.sha256_file(ROOT / res["artifact"]), expires_at=None)
            Q.record_stage(fid, "recap", {"status": it["status"], "artifact": rel,
                                          "queue_item": it["item_id"], "run_id": run.run_id},
                           lang=obj.get("language"))
        n_fail = sum(1 for v in report.values() if v)
        run.finish("ok" if n_fail == 0 else "partial", guard_summary="%d/%d clean" % (len(report) - n_fail, len(report)))
    else:
        run.finish("ok", guard_summary="frame only (--skip-generate or no narratives)")
    print("recap %s: frame=%s narratives=%d · run %s" % (fid, res["artifact"], len(arts), run.run_id))
    return 0


# ── bundle ───────────────────────────────────────────────────────────────────
def cmd_bundle(args):
    fid = args.fixture
    run = Q.RunManifest("bundle", [fid])
    if fid not in BUNDLED_IMPORT_IDS:
        run.finish("blocked")
        print("bundle %s: fixture is NOT in the frontend static-import map — engineer import step "
              "required first (design §2 decision 2; P1 = import.meta.glob)." % fid)
        return 2
    mins, _ = _minutes_to_kickoff(fid)
    copied, refused, written = [], [], set()
    # source order matters: trial narratives (NARR) win over older PROOF artifacts for the
    # same (fixture, lang) destination — a destination is written at most once per run.
    for lang in LANGS:
        for src_base, dst_base, prematch in ((NARR, FE_NARR, True), (RESCORE_MODELS, FE_RESCORE, True),
                                             (PROOF, FE_NARR, False)):
            src = src_base / ("%s.%s.deepseek.json" % (fid, lang))
            if not src.exists():
                continue
            dst = dst_base / ("%s.%s.json" % (fid, lang))
            if dst in written:
                continue
            obj = Q.read_json(src)
            if obj.get("llm_provider") == "mock":
                refused.append((src.name, "mock"))
                continue
            errs = _check_artifact(src)  # per-surface dispatch (rescore models != narrative contract)
            if errs:
                refused.append((src.name, "guard-fail"))
                continue
            if prematch and obj.get("mode") == "pre_match_2026_modeling" and mins is not None and mins <= 0:
                refused.append((src.name, "expired (kickoff passed)"))
                continue
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            written.add(dst)
            copied.append(str(dst.relative_to(ROOT)))
    run.step("copy", "ok", detail="%d copied, %d refused" % (len(copied), len(refused)),
             artifact_paths=copied)
    run.finish("ok" if copied else "failed")
    print("bundle %s: copied %d, refused %s" % (fid, len(copied), refused or "none"))
    print("REMINDER: npm build + scripts/check_customer_visible_copy.py before any deploy; "
          "deploy itself needs the Owner-conditioned flow.")
    return 0 if copied else 1


# ── queue & status ───────────────────────────────────────────────────────────
def cmd_queue(args):
    Q.sweep()
    a = args.action
    if a == "list":
        items = Q.list_items(fixture=args.fixture, status=args.status)
        for it in items:
            print("%-12s %-46s exp=%s" % (it["status"], it["item_id"], it.get("expires_at") or "-"))
        print("(%d items)" % len(items))
    elif a == "show":
        print(json.dumps(Q.load_item(args.item), ensure_ascii=False, indent=2))
    elif a == "approve":
        it = Q.approve(args.item, args.by, note=args.note)
        print("approved %s by %s" % (it["item_id"], args.by))
    elif a == "reject":
        it = Q.reject(args.item, args.by, args.note)
        print("rejected %s" % it["item_id"])
    elif a == "mark-sent":
        it = Q.mark_sent(args.item, args.by, args.channel, args.group, args.screenshot)
        print("sent recorded for %s (%s/%s)" % (it["item_id"], args.channel, args.group))
    elif a == "sweep":
        swept = Q.sweep()
        print("swept %d items: %s" % (len(swept), swept or "-"))
    return 0


def cmd_status(args):
    fid = args.fixture
    m = Q.load_manifest(fid)
    print("fixture %s · %s · kickoff %s · key=%s (%s) · lineups_released=%s" % (
        fid, m.get("match"), m.get("kickoff_utc"), m.get("key_match"),
        ",".join(m.get("key_reasons") or []), m.get("lineups_released")))
    q = m.get("quota_ledger_day") or {}
    if q:
        print("quota %s: %s/%s" % (q.get("date"), q.get("requests"), q.get("daily_budget")))
    for stage, v in (m.get("stages") or {}).items():
        if isinstance(v, dict) and any(k in LANGS for k in v):
            for lang, sv in v.items():
                print("  %-22s %-6s %-14s %s" % (stage, lang, sv.get("status"), sv.get("artifact", "")))
        else:
            print("  %-22s %s" % (stage, json.dumps(v, ensure_ascii=False)[:120]))
    items = Q.list_items(fixture=fid)
    print("queue items: %d" % len(items))
    for it in items:
        print("  %-12s %s" % (it["status"], it["item_id"]))
    return 0


def main():
    ap = argparse.ArgumentParser(prog="mvp2_ops.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("scan"); p.add_argument("--date"); p.set_defaults(fn=cmd_scan)

    p = sub.add_parser("prematch")
    p.add_argument("--fixture", required=True)
    p.add_argument("--langs")
    p.add_argument("--providers", default="deepseek")
    p.add_argument("--register-existing", action="store_true",
                   help="skip generation; guard + register + send-kit from existing artifacts")
    p.set_defaults(fn=cmd_prematch)

    p = sub.add_parser("watch")
    p.add_argument("--fixture", required=True)
    p.add_argument("--interval", type=int, default=300)
    p.add_argument("--once", action="store_true")
    p.add_argument("--no-auto", action="store_true")
    p.add_argument("--langs")
    p.set_defaults(fn=cmd_watch)

    p = sub.add_parser("rescore")
    p.add_argument("--fixture", required=True)
    p.add_argument("--langs")
    p.set_defaults(fn=cmd_rescore)

    p = sub.add_parser("recap")
    p.add_argument("--fixture", required=True)
    p.add_argument("--langs")
    p.add_argument("--skip-generate", action="store_true")
    p.set_defaults(fn=cmd_recap)

    p = sub.add_parser("bundle")
    p.add_argument("--fixture", required=True)
    p.set_defaults(fn=cmd_bundle)

    p = sub.add_parser("queue")
    p.add_argument("action", choices=["list", "show", "approve", "reject", "mark-sent", "sweep"])
    p.add_argument("item", nargs="?")
    p.add_argument("--fixture")
    p.add_argument("--status")
    p.add_argument("--by", default="operator")
    p.add_argument("--note")
    p.add_argument("--channel")
    p.add_argument("--group")
    p.add_argument("--screenshot")
    p.set_defaults(fn=cmd_queue)

    p = sub.add_parser("status")
    p.add_argument("--fixture", required=True)
    p.set_defaults(fn=cmd_status)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
