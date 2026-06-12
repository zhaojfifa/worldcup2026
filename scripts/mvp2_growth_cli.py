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

NOTHING here sends anything; MTC stays 平台积分（不可提现/不可转让/不可交易）.
"""
import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.database import SessionLocal, init_db  # noqa: E402
from app.services.growth import growth_service as G  # noqa: E402


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
    a = ap.parse_args()

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
