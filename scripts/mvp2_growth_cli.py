#!/usr/bin/env python3
"""
Growth P1 operator CLI — Intelligence Ambassador（情报官）administration.

Talks DIRECTLY to the database through the backend service layer (same code path as the
admin API; every mutation writes an audit row; caps + manual-review rules enforced there).
Set DATABASE_URL to target a DB (defaults to backend/.env via app.config).

  create-code   --code QG-AB12 [--alias 名字] [--lang zh] [--channel telegram_group_1] [--by 运营名]
  stats                                         # dashboard counts per code + pending queues
  confirm-intent --id 3 --decision confirmed|rejected [--by 运营名]
  create-contribution --code QG-AB12 --points 2 --reason content_share [--note ...] [--by 运营名]
  review-contribution --id 5 --decision approved|rejected [--note ...] [--by 运营名]
  export        [--out docs/data_audit/mvp2_growth_reports/<date>.json]
  package       today|recap|next [--fixture ID] [--lang zh|vi|my] [--ref CODE]
                # assembles a share package from BUNDLED guard-passed LLM narratives
                # (judgement lines verbatim; Owner framing; link carries the ref)

NOTHING here sends anything; MTC stays 平台积分（不可提现/不可转让/不可交易）.
"""
import argparse
import json
import re
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.database import SessionLocal, init_db  # noqa: E402
from app.services.growth import growth_service as G  # noqa: E402

# ── share packages (Growth P1.1) — mirrors frontend/src/growth/shareTemplates.ts ──
SITE = "https://worldcup2026-izid.onrender.com"
NARR_DIR = ROOT / "frontend" / "src" / "data" / "productNarratives"
LANG_FILE = {"zh": "zh-CN", "vi": "vi-VN", "my": "my-MM"}
DEFAULT_REF = {"zh": "QG-TEST1", "vi": "TT-VN88", "my": "FO-MM21"}
FIXTURES = {"1489369": {"title": "Mexico vs South Africa", "kickoff": "2026-06-11 19:00"},
            "1489371": {"title": "Brazil vs Morocco", "kickoff": "2026-06-13 22:00"}}
PERSONA = {"zh": "俅哥", "vi": "Tiên Tri Bóng Đá", "my": "Football Oracle"}


def _narr(fid, lang):
    p = NARR_DIR / ("%s.%s.json" % (fid, LANG_FILE[lang]))
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _link(path, lang, ref):
    return "%s%s%sref=%s" % (SITE, path, "&" if "?" in path else "?", ref or DEFAULT_REF[lang])


def _split_band(scoreline_view):
    """First listed score = 主比分, rest = 备选. Parsing only — the band itself is the narrative model's judgement, untouched."""
    scores = re.findall(r"\d+\s*[-–]\s*\d+", scoreline_view or "")
    scores = [re.sub(r"\s", "", s) for s in scores]
    return (scores[0], scores[1:]) if scores else (None, [])



def build_package(kind, fid, lang, ref):
    n = _narr(fid, lang)
    if not n:
        raise ValueError("no bundled narrative for %s %s" % (fid, lang))
    title = FIXTURES.get(fid, {}).get("title", fid)
    top_var = ((n.get("watch_next_signals") or n.get("risk_factors") or [{}])[0]).get("name", "")
    video_script = None
    if kind in ("today", "next"):
        if n.get("mode") == "real_recap":
            raise ValueError("%s already finished — use 'package recap'" % fid)
        link = _link("/predict/%s" % fid, lang, ref)
        head = {"today": {"zh": "今晚主看", "vi": "Trận đáng xem", "my": "ဒီညအဓိကပွဲ"},
                "next": {"zh": "即将开赛", "vi": "Sắp đá", "my": "မကြာမီ"}}[kind][lang]
        primary, alts = _split_band(n["scoreline_view"])
        why = n.get("hero_subtitle", "")
        # STRONG RESULT FIRST (Owner structure): result → 主比分/备选 → risk → why → T-30 → CTA.
        # Judgement strings stay LLM fields verbatim; only the ORDER is engineered.
        if lang == "zh":
            lines = ["%s：%s（%s UTC）" % (head, title, FIXTURES.get(fid, {}).get("kickoff", "")),
                     "俅哥主看：%s" % n["main_lean"],
                     ("主比分：%s" % primary) if primary else n["scoreline_view"]]
            if alts:
                lines.append("备选：%s" % " / ".join(alts))
            lines.append("冷门风险：%s" % n["risk_level"])
            if why:
                lines.append("为什么：%s" % why)
            lines += ["开球前 30 分钟，首发 11 人出来后，群内更新最终倾向和比分区间。",
                      "👇进群等临场修正：", link]
            video_script = "今晚%s。俅哥主看：%s。主比分%s%s。冷门风险：%s。记住一句话：赛前看方向，临场看变量。开球前30分钟，首发一出来，群内更新最终倾向。想跟住更新，进群。" % (
                title, n["main_lean"], primary or "", ("，备选%s" % "、".join(alts)) if alts else "", n["risk_level"])
        elif lang == "vi":
            lines = ["%s: %s (%s UTC)" % (head, title, FIXTURES.get(fid, {}).get("kickoff", "")),
                     "Tiên Tri chốt: %s" % n["main_lean"],
                     ("Tỷ số chính: %s" % primary) if primary else n["scoreline_view"]]
            if alts:
                lines.append("Phương án phụ: %s" % " / ".join(alts))
            lines.append("Rủi ro bất ngờ: %s" % n["risk_level"])
            if why:
                lines.append("Vì sao: %s" % why)
            lines += ["Đội hình công bố là nhóm cập nhật thiên hướng cuối + vùng tỷ số, 30 phút trước giờ đá.",
                      "👇Vào nhóm chờ hiệu chỉnh sát giờ:", link]
            video_script = "Tối nay %s. Tiên Tri chốt: %s. Tỷ số chính %s%s. Rủi ro: %s. Nhớ một câu: trước trận xem hướng, sát giờ xem biến số. 30 phút trước giờ đá, đội hình ra là nhóm cập nhật ngay. Muốn theo kịp, vào nhóm." % (
                title, n["main_lean"], primary or "", (", phụ %s" % ", ".join(alts)) if alts else "", n["risk_level"])
        else:
            lines = ["%s: %s (%s UTC)" % (head, title, FIXTURES.get(fid, {}).get("kickoff", "")),
                     "Oracle ပြတ်ပြတ်: %s" % n["main_lean"],
                     ("အဓိကစကော: %s" % primary) if primary else n["scoreline_view"]]
            if alts:
                lines.append("အရန်: %s" % " / ".join(alts))
            lines.append("Risk: %s" % n["risk_level"])
            if why:
                lines.append("ဘာကြောင့်: %s" % why)
            lines += ["Lineup ထွက်တာနဲ့ ပွဲမစခင် မိနစ် ၃၀ မှာ အဖွဲ့ထဲ နောက်ဆုံးအမြင် တင်မည်။",
                      "👇အဖွဲ့ဝင်ရန်:", link]
            video_script = "ဒီည %s။ Oracle ပြတ်ပြတ်: %s။ အဓိကစကော %s%s။ Risk: %s။ မှတ်ထားပါ — ပွဲကြို ဦးတည်ချက်၊ ပွဲနီး variable။ ပွဲမစခင် မိနစ် ၃၀ lineup ထွက်တာနဲ့ အဖွဲ့ထဲ update တင်မည်။ လိုက်ကြည့်ချင်ရင် အဖွဲ့ဝင်ပါ။" % (
                title, n["main_lean"], primary or "", ("၊ အရန် %s" % ", ".join(alts)) if alts else "", n["risk_level"])
        meta = {"fixture_id": fid, "title": title, "strong_pick": n["main_lean"],
                "primary_scoreline": primary, "alternative_scorelines": alts,
                "scoreline_band": n["scoreline_view"], "risk_label": n["risk_level"],
                "top_variable": top_var, "share_link": link}
    else:  # recap — structure: result → what was right → what changed → learn → next hook
        if n.get("mode") != "real_recap":
            raise ValueError("%s has no real recap narrative" % fid)
        link = _link("/recap/%s" % fid, lang, ref)
        right = ((n.get("validated_factors") or [{}])[0]).get("name", "")
        changed = ((n.get("underweighted_factors") or [{}])[0]).get("name", "")
        head = {"zh": "俅哥复盘", "vi": "Tiên Tri phục dựng", "my": "Oracle ပြန်သုံးသပ်ချက်"}[lang]
        right_lbl = {"zh": "抓对了什么", "vi": "Bắt đúng", "my": "မှန်ခဲ့သည်"}[lang]
        learn = {"zh": "学到什么：赛前看方向，临场看变量，赛后看校准。",
                 "vi": "Bài học: trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh.",
                 "my": "သင်ခန်းစာ: ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်။"}[lang]
        nxt = {"zh": "下一场 Brazil vs Morocco，开球前 30 分钟继续看首发修正。\n👇进群看临场修正：",
               "vi": "Trận tới Brazil vs Morocco, tiếp tục xem hiệu chỉnh đội hình 30 phút trước giờ đá.\n👇Vào nhóm:",
               "my": "နောက်ပွဲ Brazil vs Morocco — မိနစ် ၃၀ lineup ပြန်တွက်ချက် ဆက်ကြည့်ပါ။\n👇အဖွဲ့ဝင်ရန်:"}[lang]
        lines = ["%s：%s" % (head, n["short_title"])]
        if right:
            lines.append("%s：%s" % (right_lbl, right))
        lines += [n["screenshot_line"], learn, nxt, link]
        video_script = {"zh": "%s。%s。%s 下一场 Brazil vs Morocco，开球前30分钟，首发出来群内重算。想看，进群。" % (
                            n["short_title"], n["screenshot_line"], learn),
                        "vi": "%s. %s. %s Trận tới Brazil vs Morocco — nhóm tính lại 30 phút trước giờ đá. Vào nhóm." % (
                            n["short_title"], n["screenshot_line"], learn),
                        "my": "%s။ %s။ နောက်ပွဲ Brazil vs Morocco — မိနစ် ၃၀ ပြန်တွက်မည်။ အဖွဲ့ဝင်ပါ။" % (
                            n["short_title"], n["screenshot_line"])}[lang]
        meta = {"fixture_id": fid, "recap_line": n["screenshot_line"], "what_was_right": right,
                "what_changed_score": changed, "next_fixture_hook": "1489371 Brazil vs Morocco T-30",
                "share_link": link}
    return {"kind": kind, "lang": lang, "ref": ref or DEFAULT_REF[lang],
            "copy_text": "\n".join(lines), "video_script_30s": video_script, "meta": meta}


# ── refresh wrapper (P1.1b): all packages, per-package status, file output ──
PKG_DIR = ROOT / "docs" / "data_audit" / "mvp2_growth_packages"
QUEUE_JSON = ROOT / "docs" / "data_audit" / "mvp2_review_queue" / "queue.json"
DEFAULT_FIXTURE = {"today": "1489371", "next": "1489371", "recap": "1489369"}


def _recap_approval_status(fid, lang):
    """Simple read-only queue lookup: best status among recap items for fixture+lang.
    Returns 'approved' | 'guard_passed' | ... | 'unknown' (never blocks generation)."""
    try:
        items = json.loads(QUEUE_JSON.read_text(encoding="utf-8")).get("items", {})
        prefix = "%s.recap.%s." % (fid, LANG_FILE[lang])
        states = [v.get("status") for k, v in items.items() if k.startswith(prefix)]
        for want in ("sent", "approved", "guard_passed", "needs_review"):
            if want in states:
                return want
        return states[-1] if states else "unknown"
    except Exception:
        return "unknown"


def _share_card_url(kind, fid, lang, ref):
    path = "/share/recap/%s" % fid if kind == "recap" else "/share/fixture/%s" % fid
    return "%s%s?ref=%s&lang=%s" % (SITE, path, ref or DEFAULT_REF[lang], lang)


def cmd_refresh(lang, ref, stamp):
    ref = (ref or DEFAULT_REF[lang]).upper()
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"lang": lang, "ref": ref, "generated_at": stamp, "packages": {}}
    for kind in ("today", "next", "recap"):
        fid = DEFAULT_FIXTURE[kind]
        entry = {"fixture_id": fid}
        try:
            doc = build_package(kind, fid, lang, ref)
        except ValueError as e:
            reason = str(e)
            entry["status"] = "needs_fixture" if "no bundled narrative" in reason else "refused"
            entry["reason"] = reason
            summary["packages"][kind] = entry
            print("%-6s %-12s %s (%s)" % (kind, entry["status"], fid, reason))
            continue
        except FileNotFoundError as e:
            entry.update(status="unavailable", reason=str(e))
            summary["packages"][kind] = entry
            print("%-6s unavailable  %s" % (kind, fid))
            continue
        status_lines = ["package_status: available"]
        if kind == "recap":
            ap = _recap_approval_status(fid, lang)
            entry["approval_status"] = ap
            status_lines.append("approval_status: %s" % ap)
            if ap not in ("approved", "sent"):
                entry["warning"] = "Verify queue approval before sending."
                status_lines.append('warning: "Verify queue approval before sending."')
        card_url = _share_card_url(kind, fid, lang, ref)
        fname = "%s_%s_%s_%s.md" % (kind, fid, lang, ref)
        body = "\n".join([
            "# Growth package · %s · %s · %s" % (kind, fid, lang),
            "",
            "- fixture_id: %s" % fid,
            "- lang: %s" % lang,
            "- ref: %s" % ref,
            "- share_link: %s" % doc["meta"]["share_link"],
            "- share_card_url: %s" % card_url,
            "- " + "\n- ".join(status_lines),
            "- generated_at: %s" % stamp,
            "- operator_next_step: 人工审核文案 → Owner GO（fixture+channel）→ 手动粘贴发送 →"
            " queue mark-sent + 截图 + SEND_LOG（绝不自动发送）",
            "",
            "## copy_text（原样粘贴；只允许替换群链接占位）",
            "```text",
            doc["copy_text"],
            "```",
        ] + ([
            "",
            "## video_script_30s（口播稿 · 可选）",
            "```text",
            doc.get("video_script_30s") or "",
            "```",
        ] if doc.get("video_script_30s") else [])) + "\n"
        (PKG_DIR / fname).write_text(body, encoding="utf-8")
        entry.update(status="available", file=str((PKG_DIR / fname).relative_to(ROOT)),
                     share_link=doc["meta"]["share_link"], share_card_url=card_url)
        summary["packages"][kind] = entry
        print("%-6s available    %s -> %s" % (kind, fid, fname))
    sp = PKG_DIR / ("refresh_summary_%s.json" % stamp)
    sp.write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("summary -> %s" % sp.relative_to(ROOT))
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create-code")
    c.add_argument("--code", required=True); c.add_argument("--alias", default="")
    c.add_argument("--lang", default="zh"); c.add_argument("--channel", default=None)
    c.add_argument("--by", default="operator")
    sub.add_parser("stats")
    ci = sub.add_parser("confirm-intent")
    ci.add_argument("--id", type=int, required=True); ci.add_argument("--decision", required=True)
    ci.add_argument("--by", default="operator")
    cc = sub.add_parser("create-contribution")
    cc.add_argument("--code", required=True); cc.add_argument("--points", type=int, required=True)
    cc.add_argument("--reason", required=True); cc.add_argument("--note", default="")
    cc.add_argument("--by", default="operator")
    rc = sub.add_parser("review-contribution")
    rc.add_argument("--id", type=int, required=True); rc.add_argument("--decision", required=True)
    rc.add_argument("--note", default=""); rc.add_argument("--by", default="operator")
    ex = sub.add_parser("export")
    ex.add_argument("--out", default=None)
    pk = sub.add_parser("package")
    pk.add_argument("kind", choices=["today", "recap", "next"])
    pk.add_argument("--fixture", default=None)
    pk.add_argument("--lang", default="zh", choices=["zh", "vi", "my"])
    pk.add_argument("--ref", default=None)
    rf = sub.add_parser("refresh")
    rf.add_argument("--lang", default="zh", choices=["zh", "vi", "my"])
    rf.add_argument("--ref", default=None)
    a = ap.parse_args()

    if a.cmd == "refresh":
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        cmd_refresh(a.lang, a.ref, stamp)
        return

    if a.cmd == "package":
        # pure file assembly — no DB needed; default fixtures: today/next=1489371, recap=1489369
        fid = a.fixture or ("1489369" if a.kind == "recap" else "1489371")
        try:
            doc = build_package(a.kind, str(fid), a.lang, a.ref)
        except ValueError as e:
            print("REFUSED: %s" % e)
            sys.exit(1)
        print(json.dumps(doc["meta"], ensure_ascii=False, indent=1))
        print("\n---- copy_text (paste-ready) ----\n%s" % doc["copy_text"])
        if doc.get("video_script_30s"):
            print("\n---- video_script_30s (spoken) ----\n%s" % doc["video_script_30s"])
        return

    init_db()
    db = SessionLocal()
    try:
        if a.cmd == "create-code":
            amb = G.create_ambassador(db, a.code, a.alias, a.lang, a.channel, a.by)
            print("created %s (%s) status=%s" % (amb.code, amb.display_alias or "-", amb.status))
        elif a.cmd == "stats":
            print(json.dumps(G.dashboard(db), ensure_ascii=False, indent=1))
        elif a.cmd == "confirm-intent":
            it = G.confirm_intent(db, a.id, a.decision, a.by)
            print("intent #%d -> %s (pending contribution auto-created on confirm)" % (it.id, it.confirm_status))
        elif a.cmd == "create-contribution":
            cn = G.create_contribution(db, a.code, a.points, a.reason, a.note, a.by)
            print("contribution #%d pending (%d 贡献值, %s) — requires review before any MTC credit"
                  % (cn.id, cn.points, cn.reason))
        elif a.cmd == "review-contribution":
            cn = G.review_contribution(db, a.id, a.decision, a.by, a.note)
            print("contribution #%d -> %s token_log_id=%s" % (cn.id, cn.status, cn.token_log_id))
        elif a.cmd == "export":
            doc = G.export_report(db)
            out = pathlib.Path(a.out) if a.out else ROOT / "docs" / "data_audit" / "mvp2_growth_reports" / (
                "growth_report_%s.json" % datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ"))
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print("exported -> %s" % out)
    except ValueError as e:
        print("REFUSED: %s" % e)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
