# Giành Cup · Accelerated MVP Operation Loop

_Version: MVP v0.7 · Created: 2026-06-06_

Supersedes the pacing (not the content) of `docs/MVP_7_DAY_LOOP_PLAN.md`.
The original 7-day plan is **retained as reference**; execution is compressed into
**3 days of intensive operating validation + 1 unified review day**.

Execution log: append results to `docs/MVP_7_DAY_LOG.md` (Day A/B/C/D sections).

Compliance floor (every day): 不做博彩 · 不做现金投注 · 不承诺命中 · 不承诺收益 ·
MTC 仅平台积分（不可提现/不可转让/不可交易）· 排行榜是连胜/积分榜，不是收益榜。

---

## 1. Why accelerate

- The engineering base is **already at MVP v0.7** (5 pages, full API surface, R2,
  streak/rankings, community heat, compliance docs — Day 1 verified PASS).
- The bottleneck is **no longer page count or endpoint count**.
- The decisive factors now are **operational**, not structural:
  1. **Copy attractiveness** — does the content pull users in?
  2. **Modeling credibility** — are AI viewpoints believable?
  3. **Community承接** — is a real community established that can receive users?
  4. **Operating cadence** — can we produce content reliably every day?
  5. **Retention** — does MTC / streak give users a reason to return?

So we stop the slow 7-day cadence and run a tight A/B/C/D loop that puts content,
community, and retention under real (small) traffic fast — **without skipping service
verification or compliance, and without jumping to LLM**.

---

## 2. Day A — Service & Data-Source Fast Acceptance

**Goal:** complete the core of the original Day 1 + Day 2 in a single day.

**Checks:**
- Frontend 5 pages reachable (Home / Detail / Report / Token / Community).
- `GET /health` · `GET /matches` · `GET /reports/{id}`.
- `GET /assets/status`.
- `GET /social/channels`.
- `GET /community/heat`.
- `GET /users/1/streak` · `GET /rankings`.
- `GET /data-source/status`.
- `POST /admin/sync/fixtures` (admin token).
- `POST /admin/sync/results` (admin token; `{league_id, season}`).
- `POST /matches/{id}/refresh`.
- `GET /performance/summary`.

**Output — classify every capability:**
- **Real** — backed by live data / real persistence.
- **Mock / demo** — seed or mock-mode fallback.
- **Operational impact** — which of the above blocks or limits the small-traffic trial.

> Day 1 already verified the read endpoints + event loop (see `MVP_7_DAY_LOG.md`).
> Day A adds the **write/data-source path** (`sync/fixtures`, `sync/results`, `refresh`,
> `performance/summary`) and the real-vs-mock classification.

---

## 3. Day B — Operating Content & Community承接

**Goal:** verify copy can attract and community can receive users.

### Four mandatory human-authored templates (no LLM)

**1. 今日 AI 三场速览**
- 比赛（队伍 vs 队伍）
- AI 倾向（方向 + 简述）
- 信心星级（★–★★★★★）
- 一句话理由
- 风险提示
- 引导进入社群（CTA）

**2. 爆冷风险 TOP3**
- 比赛
- 爆冷风险点
- 为什么值得关注
- 风险免责声明（历史表现不代表未来结果…）

**3. 临场修正模板**
- 触发因素（首发/伤停/天气…）
- 胜率变化（before → after）
- AI 调整原因
- 社群提醒话术

**4. 赛后复盘模板**
- AI 原始观点
- 实际结果
- 判断是否命中
- 误差来源
- 下一场修正方向

Every template: 「AI 倾向 / AI 数据观点」framing (never result promises),
disclaimer where 战绩/命中/连胜 appears, passes forbidden-word scan.

### Community承接 verification
- Zalo — does a **real** link exist?
- Telegram — does a **real** link exist?
- If no real links → at minimum stand up a **test group**.
- `POST /admin/social/channels/upsert` — can a channel be set to `active` with a `public_url`?
- Click → `click_social_channel` event recorded (`POST /events/track`)?
- `GET /community/heat` updates after clicks?

**Output:** 4 finalized templates + community status (real link / test group / blocked).

---

## 4. Day C — MTC / Retention / Compliance / Small-Traffic Trial

**Goal:** verify users have a reason to return.

### Retention loop checks
- Check-in (`POST /tokens/checkin`).
- Free challenge join (`POST /challenges/{id}/join`).
- Admin settle (`POST /admin/challenges/settle`, options `A/B/neutral`).
- Streak grows on correct, resets on miss, unchanged on neutral.
- Rankings update (sort current → best → mtc_earned).
- MTC reward credited (+10 correct; +20 at streak 3; +80 at streak 7).
- MTC 不可提现 statement present.
- Rankings confirmed **non-earnings board**.

### Small-traffic trial
- Select **3 matches**.
- Generate **3 operating posts** from Day B templates.
- Publish to test group / internal group.
- Record:
  - clicks
  - social-channel entry clicks
  - unlock-CTA clicks
  - user feedback
  - **which post was most attractive**

**Output:** retention loop verified + trial metrics + "most attractive copy" finding.

---

## 5. Day D — Unified Review

**Review dimensions:**
1. Copy attractiveness.
2. AI result credibility.
3. Data-source reliability.
4. Community承接 capability.
5. MTC retention value.
6. Compliance risk.
7. Decision: enter Day 8 LLM or not.

### Enter Day 8 (LLM) **only if ALL hold:**
- Service stable.
- At least one round of operating-copy trial completed.
- Community entry usable (real link or test group).
- Forbidden-word scan process stable.
- Human templates exist for the LLM to learn from.

### Do **NOT** enter Day 8 if **any** hold:
- Data source still unclear.
- Community entry not established.
- Copy has no test feedback.
- Compliance process unstable.

> When Day 8 starts, LLM (Kimi/DeepSeek) for AI explanation must ship **behind a
> banned-word output filter** before any generated text reaches users.

---

## 6. Key ruling

- ✅ Accelerate operating validation now.
- ❌ Do **not** skip service verification.
- ❌ Do **not** skip compliance checks.
- ❌ Do **not** go straight to LLM.
- ⏳ LLM starts **only after the Day D review** approves it.

---

## 7. Boundaries (entire accelerated loop)

No new features · no LLM (until Day D approval) · no payments · no bots · no UGC /
user uploads · no new pricing tiers · no changes to `/matches`, `/matches/{id}`,
`/reports/{id}` response shapes · admin writes token-protected · never log/commit secrets.
