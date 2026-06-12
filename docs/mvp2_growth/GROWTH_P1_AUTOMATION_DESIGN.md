# Growth P1 — Intelligence Ambassador Automation Design（情报官推广机制）

> Branch `feature/mvp2-growth-p1-automation` @ main 6b56725. Owner GO for automation design;
> implementation starts only after Owner accepts this design. Framing: **Intelligence Ambassador**
> （俅哥情报官 / Tiên Tri Ambassador / Football Oracle Ambassador）— attention + contribution,
> NEVER betting/commission/payout. MTC stays 平台积分（不可提现/不可转让/不可交易）.

## 1. User journey

```
Ambassador (operator-issued code, e.g. QG-AB12)
  → opens own 情报链 link or 专属二维码 (e.g. /predict/1489371?ref=QG-AB12)
  → shares card + link/QR into their circle (manual share; no auto-send)
New fan
  → lands on /join?ref=QG-AB12 (or any product surface carrying ?ref=)
  → ref code captured (localStorage, 30-day soft window) + click recorded (no PII)
  → reads landing value prop: 赛前强判断 · 30分钟临场修正 · 赛后复盘校准
  → taps 进群看临场修正 → join-intent recorded → group link (operator-configured) opens
Operator
  → dashboard: clicks / join-intents / manual-confirmed joins per code+channel
  → grants 贡献值 (pending) → reviews → approve = MTC credit via existing wallet_service
Owner
  → monthly 月度榜单 (contribution leaderboard, points only, no cash anywhere)
```

## 2. Ambassador role model
- Codes are **operator-issued only** (no self-serve signup in P1) via CLI; format
  `{persona-prefix}-{4..6 alnum}`: `QG-…` (zh), `TT-…` (vi), `FO-…` (my).
- Stored fields: code, display_alias (persona-safe nickname, no real name required), language,
  default channel_tag, status (active/paused/retired), created_by, created_at.
- An ambassador is NOT a User account (DEMO_USER_ID=1 reality unchanged); a shadow User row is
  created ONLY when MTC is granted (reuses existing wallet/TokenLog rails, mirroring the accepted
  Track B P0 decision).
- No hierarchy: codes have no parent/child; no override, no downline, no tiering — ever.

## 3. Invite link / QR flow
- Link forms: `/join?ref=<code>` (primary) · `/predict/<fid>?ref=<code>` · `/recap/<fid>?ref=<code>`.
- `ref` is read client-side on any route, persisted to localStorage (`growth_ref`, 30 days,
  first-touch wins; overwrite only with `?ref_force=1` operator testing flag).
- QR: generated **server-side in the admin preview only** (operator downloads PNG; QR is never
  rendered to customers). QR target = the link above, nothing else encoded.
- Group link on /join is **operator-configured static config** (env/admin setting), shown after
  join-intent tap; engineering never hardcodes a group URL in copy.

## 4. Attribution model
- **Click**: one row per landing with ref (code, surface, lang, optional channel_tag if the
  ambassador appended `&ch=<allowed-tag>`, ts, coarse device class mobile/desktop). Dedup: same
  localStorage session re-landing within 30 min = not a new click.
- **Join-intent**: tap on the group CTA with the stored ref (code, surface, lang, ts).
- **Confirmed join**: MANUAL — operator compares group member delta and confirms intents in the
  dashboard (P1 has no in-group bot; no automatic confirmation).
- Channel-level + code-level only. First-touch attribution; no cross-device identity, no
  fingerprinting, no cookies beyond localStorage.

## 5. Data model (new tables, additive only; no existing shape changes)

```
growth_ambassadors   id PK · code UNIQUE · display_alias · lang · default_channel ·
                     status · created_by · created_at
growth_clicks        id PK · ambassador_id FK · surface · lang · channel_tag NULL ·
                     device_class · created_at            (NO ip, NO ua string, NO user id)
growth_join_intents  id PK · ambassador_id FK · surface · lang · created_at ·
                     confirm_status (unconfirmed|confirmed|rejected) · confirmed_by NULL ·
                     confirmed_at NULL
growth_contributions id PK · ambassador_id FK · points INT · reason ENUM(confirmed_join|
                     content_share|monthly_bonus|other) · note · status (pending|approved|
                     rejected) · created_by · reviewed_by NULL · reviewed_at NULL ·
                     token_log_id NULL (set on approve→wallet credit) · created_at
growth_audit_log     id PK · actor · action · entity_type · entity_id · before_json ·
                     after_json · created_at              (append-only; no UPDATE/DELETE path)
```
No money/price/odds columns exist or can exist; points are INT MTC only.

## 6. API endpoints (additive; existing API shapes untouched)

| Method/Path | Auth | Purpose |
|---|---|---|
| POST `/api/v1/growth/click` | public, rate-limited | record landing {ref, surface, lang, ch?} |
| POST `/api/v1/growth/join-intent` | public, rate-limited | record group-CTA tap {ref, surface, lang} |
| GET `/api/v1/admin/growth/dashboard` | x-admin-token | per-code: clicks/intents/confirmed/sends/points/pending |
| POST `/api/v1/admin/growth/ambassadors` | x-admin-token | create code |
| PATCH `/api/v1/admin/growth/ambassadors/{code}` | x-admin-token | pause/retire |
| POST `/api/v1/admin/growth/intents/{id}/confirm` | x-admin-token | manual join confirm/reject |
| POST `/api/v1/admin/growth/contributions` | x-admin-token | create pending grant |
| POST `/api/v1/admin/growth/contributions/{id}/review` | x-admin-token | approve(→wallet credit)/reject, note required |
| GET `/api/v1/admin/growth/export` | x-admin-token | weekly growth report JSON (counts only) |

Invalid/unknown ref = recorded as `invalid_ref` counter, no row against any ambassador.
Admin routes locked exactly like existing admin (401 without ADMIN_API_TOKEN).

## 7. Frontend surfaces
- **`/join`** (new route): persona hero（俅哥带你看球 / 赛前看方向，临场看变量，赛后看校准）+
  three value rows（赛前强判断 · 30分钟临场修正 · 赛后复盘校准, fixed Owner vocabulary）+
  进群看临场修正 CTA + disclaimer footer. zh/vi/my. Scanner adds this surface (21 surfaces).
- **ref capture** in App bootstrap (all routes).
- **Share-card preview + QR**: inside the EXISTING admin/ops fold (`?ops=1`) and the operator
  dashboard — renders the live strong-call/recap card block + the ambassador link + QR download.
  Customers never see QR or ref machinery.
- **Operator dashboard**: admin-gated page (x-admin-token entry like /internal/scout-pack):
  table per code (clicks/intents/confirmed/points/pending review queue with approve/reject).

## 8. Operator dashboard (content spec)
Columns: code · alias · lang · channel · clicks(7d/total) · join-intents · confirmed joins ·
contribution points (approved/pending) · last activity. Actions: confirm/reject intents,
approve/reject contributions (note required on reject), pause code, export report.
Leaderboard view = 月度榜单 by approved points (积分/贡献榜, never 收益榜; disclaimer pinned).

## 9. MTC contribution ledger
- Points enter as **pending** (auto-suggested by rule, e.g. confirmed_join = 10 贡献值; rates are
  operator-configurable constants, Owner-approved before launch).
- **Manual review required** for every grant; approve → existing `wallet_service._credit` →
  TokenLog with reason `growth_contribution` (auditable); reject → audit row, nothing credited.
- Caps: per-ambassador daily cap + monthly cap (constants, Owner sets values).
- MTC remains 平台积分: 不可提现 · 不可转让 · 不可交易 · 不作为金融资产 · no cash mapping anywhere.
- No automatic settlement of anything; no points tied to match outcomes or anyone's "winnings".

## 10. Guard rules (implemented BEFORE surfaces ship)
- New `scripts/check_growth_copy.py`: scans /join + dashboard + share-card preview copy sources
  against the P0 guard-spec wordlists (betting/odds/handicap/bookmaker · win-guarantee ·
  commission/payout/recharge/cash-reward · agent-hierarchy · process/audit leakage; 4 languages).
- `check_customer_visible_copy.py` ROUTES += `/join` (×3 langs → 21 surfaces).
- Allowed vocabulary fixed: 情报官 · 邀请码 · 情报链 · 专属二维码 · 贡献值 · MTC 积分 · 月度榜单 ·
  渠道贡献 · 进群看临场修正 · 赛前看方向，临场看变量，赛后看校准.
- 提现 appears ONLY inside 不可提现 (existing rule).

## 11. Audit log
Every mutation (code create/pause, intent confirm, contribution create/review, wallet credit)
writes an append-only `growth_audit_log` row with actor + before/after. No silent mutation: the
service layer has no UPDATE path that bypasses audit. Weekly export includes audit counts.

## 12. Privacy note
We record: ref code, surface, language, timestamp, coarse device class, operator-entered channel
tags. We do NOT record: names, phones, emails, IPs, user agents, device IDs, group member
identities, message contents. Confirmed joins are operator-counted numbers, not identity matches.
Data lives in the existing Render Postgres; export is counts-only.

## 13. Explicitly NOT included
Betting/odds/handicap/bookmaker anything · cash commission/payout/withdrawal/recharge rebate ·
wallet cash balance · multi-level/agent hierarchy · automatic settlement · auto-send/bots ·
self-serve ambassador signup · per-user tracking/fingerprinting · QR on customer surfaces ·
push notifications (see APP_FEASIBILITY_ASSESSMENT.md) · payments of any kind.

## Implementation order (after Owner accepts)
1. Guard first (check_growth_copy + scanner /join route) → 2. DB tables + audit →
3. public click/join-intent endpoints → 4. /join page + ref capture → 5. admin endpoints →
6. operator dashboard + QR/share preview → 7. CLI (create-code / stats / review / export) →
8. build + 21-surface scan + screenshots + review doc. Each step additive; existing API shapes
untouched; nothing deploys without the Owner-conditioned flow.
