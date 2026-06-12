# Growth P1.1 — Operator Notes（情报官运营台 · 上手与分享操作）

## 1. Admin login（/internal/growth）
- The dashboard requires the **REAL backend `ADMIN_API_TOKEN`** — the exact value set in the
  **Render backend service env** (worldcup2026-api). Placeholder strings (e.g. `x-token-admin`,
  `test-token-local`) WILL fail with 401 — that is the lock working, not a bug.
- Steps: Render dashboard → backend service → Environment → copy `ADMIN_API_TOKEN` →
  open `https://worldcup2026-izid.onrender.com/internal/growth` → paste → 进入.
  (`?token=<value>` also works as an operator deep link; the token then stays in sessionStorage.)
- Never paste the token into any customer-facing chat or screenshot.

## 2. First test ambassador codes (create after login)
| code | lang | channel |
|---|---|---|
| `QG-TEST1` | zh | `zh_internal_group` |
| `TT-VN88` | vi | `telegram_vi_trusted` |
| `FO-MM21` | my | `telegram_group_1` |
Create via the 新建邀请码 box (or curl per GROWTH P1 report §11). Then verify on the live site:
1. open `/join?ref=QG-TEST1` → dashboard 点击 +1
2. tap the group CTA → dashboard 入群意向 +1 → 确认 → 贡献值 10 pending → 批准 (manual MTC credit)
3. 专属二维码 ▸ opens the QR preview; 下载 PNG works.

## 3. Share buttons (now on every key surface)
首页主推卡 · /predict 强判断卡 · 首页复盘卡 · /join — each has:
🔗 复制情报链（link carries the visitor's ref, else the per-language default code）·
📋 复制分享文案（LLM judgement lines + Owner framing, paste-ready）·
🖼️ 查看分享卡（/share/... screenshot card with QR）· 👥 加入情报群.

## 4. Share-card routes (screenshot-friendly; QR allowed HERE only)
`/share/fixture/1489371?ref=QG-TEST1&lang=zh` · `/share/recap/1489369?ref=QG-TEST1&lang=zh`
(+vi/my via `lang=`). Screenshot at mobile width; persona + disclaimer stay in frame.
QR encodes `/join?ref=<code>` — never appears on normal customer match pages.

## 5. Share package CLI（自动内容包）
```bash
python3 scripts/mvp2_growth_cli.py package today --lang zh --ref QG-TEST1          # 今日主推
python3 scripts/mvp2_growth_cli.py package recap --fixture 1489369 --lang vi --ref TT-VN88   # 最新复盘
python3 scripts/mvp2_growth_cli.py package next  --fixture 1489371 --lang my --ref FO-MM21   # 新比赛预热
```
Output = meta JSON + paste-ready copy_text. Judgement lines come verbatim from bundled
guard-passed narratives; links carry the ref. NO send happens — paste manually per the P0 SOP
(Owner GO per fixture/channel → approve → manual send → mark-sent + screenshot).

## 6. Compliance reminders
分享文案/分享卡 never contain: betting/odds/handicap/bookmaker words · win guarantees ·
commission/payout/recharge/cash rewards · agent hierarchy · model/process/audit leakage ·
fake urgency. `check_growth_copy.py` scans all share copy sources; run it after any copy change.
MTC 贡献值 = 平台积分（不可提现 · 不可转让 · 不可交易）, every credit manually reviewed.
