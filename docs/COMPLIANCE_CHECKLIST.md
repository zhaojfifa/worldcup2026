# Giành Cup · Public MVP Compliance Checklist

_Version: Day 7 · Last updated: 2026-06-06_

Use this checklist before any public launch, campaign, or copy update.
All items must pass before going live.

---

## 1. Forbidden Words — Never Appear in User-Facing Copy

Scan all UI text, push messages, and marketing copy for:

| Forbidden term | Why banned |
|----------------|-----------|
| 下注 | Gambling wording |
| 稳赚 | Guaranteed-profit claim |
| 必中 | Sure-win claim |
| 跟单 | Copy-trading wording |
| 购彩 | Lottery purchase wording |
| 回报率 | Return-rate claim |
| 返奖 | Payout / prize-return wording |
| 收益承诺 | Profit guarantee |
| 现金奖池 | Cash prize pool |
| 提现 (standalone) | Withdrawal — only allowed inside `不可提现` |
| Token 转让 | Token transfer |
| Token 交易 | Token trading |
| 包赢 / 必赢 | Guaranteed win |
| 投注 | Wagering |

**Scan command:**
```bash
grep -rn "下注\|稳赚\|必中\|跟单\|购彩\|回报率\|返奖\|收益承诺\|现金奖池\|投注\|包赢\|必赢" \
  frontend/src/
```

---

## 2. MTC (Fan Token) Compliance Statement

Every page or section displaying MTC balance, earnings, or rewards must include:

> **MTC 为平台积分 · 不可提现 · 不可转让 · 不可交易 · 不作为金融资产**

Checklist:
- [ ] Token page displays the MTC statement
- [ ] Community page subscription section includes the compliance note
- [ ] No page claims MTC has monetary exchange value
- [ ] No page offers MTC withdrawal, transfer, or trading

---

## 3. 战绩 / 命中 / 连胜 Disclaimer

Wherever historical performance, hit rate, or winning streaks are displayed:

> **历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。**

Checklist:
- [ ] Track record section on Home page carries the disclaimer
- [ ] Fan Streak card on Token page carries the disclaimer
- [ ] Rankings board carries the disclaimer
- [ ] No page implies past performance predicts future results

---

## 4. Rankings Board — Not an Earnings Board

- [ ] Rankings sort by `current_streak` → `best_streak` → `mtc_earned` (no cash column)
- [ ] Rankings page/section title does not use any earnings-related wording
- [ ] No monetary value is displayed next to usernames
- [ ] Rankings disclaimer is present: `历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。`

---

## 5. AI Viewpoints — Not Result Promises

- [ ] AI verdict copy uses「AI 倾向」/「AI 数据观点」, not「AI 预测必中」
- [ ] No copy says「AI 准确率 100%」or similar absolute claims
- [ ] Live lineup correction copy says「AI 重新计算」, not「AI 确认赢」
- [ ] Brand tagline is「不只看胜率，更看 AI 为什么这样判断」(analysis framing)

---

## 6. Community / Social Channels — Not Gambling Channels

- [ ] Zalo / Telegram channel descriptions do not reference betting, wagering, or tips
- [ ] Channel copy uses「AI 情报推送」/「临场修正实时同步」framing
- [ ] No channel description promises profits or guaranteed wins
- [ ] Subscription page footer includes: `订阅为 AI 数据分析与情报服务 · 非博彩 · 不提供现金投注 · MTC 不可提现`

---

## 7. User-Facing Display — Final Checks

- [ ] Header/hero: brand is `Giành Cup · 世界杯 AI 足球情报社区`
- [ ] No mention of `Nhà Tiên Tri AI` in user-facing copy (historical docs only)
- [ ] `VITE_USE_MOCK=true`: mock mode does not show fabricated rankings or earnings
- [ ] `VITE_USE_MOCK=false`: API mode shows live data with disclaimers
- [ ] `/matches`, `/matches/{id}`, `/reports/{id}` response shapes unchanged
- [ ] Health endpoint confirms `real_money_betting_enabled: false` and `token_withdrawal_enabled: false`

---

## 8. Environment / Backend Compliance Guards

- [ ] `ENABLE_REAL_MONEY_BETTING=false` in Render env
- [ ] `ENABLE_TOKEN_WITHDRAWAL=false` in Render env
- [ ] `ADMIN_API_TOKEN` set (admin routes locked to public if unset)
- [ ] No API key or secret committed to git (`.env` / `.env.local` in `.gitignore`)

---

## Sign-off

| Check | Verified by | Date |
|-------|-------------|------|
| Forbidden words scan | | |
| MTC statement present | | |
| Disclaimers present | | |
| Rankings non-earnings | | |
| AI copy non-promise | | |
| Community non-gambling | | |
| Build passes | | |
| Mock/API dual mode | | |
