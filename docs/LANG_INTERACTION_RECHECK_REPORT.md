# Language Interaction-State Recheck Report

**Verdict: PASS WITH ISSUES** — operator-reported Chinese unlock modal found and fixed across
zh/vi/mm/en; all interaction states (modal / action-sheet / toast) re-scanned and screenshot-verified
for mm & vi; zh and price isolation unaffected; build passes; backend untouched.

_Date: 2026-06-08. Standard: screenshot-driven QA, now extended to interaction states._

---

## 1. Trigger

Real operating feedback:
- **mm Chinese unlock modal:** after tapping unlock on `/?lang=mm` → `/detail`, the modal showed
  Chinese — `已解锁，可直接查看完整报告` (body) and `继续查看报告` (button).
- **Telegram direct open still fails** on the operator's phone (Telegram installed) but **Copy Link
  works**. Ruling: Telegram direct-open is **PASS WITH ISSUES** — copy-link is the accepted operating path.

Root insight: previous QA scanned **static page DOM only** and never opened the **modal / toast /
action-sheet / unlock** states — so a hardcoded Chinese modal slipped through. **Interaction-state
language QA is now mandatory.**

## 2. Scope

- **Interaction path (mm & vi):** unlock (cash + MTC) modal → continue → report · Telegram active-channel
  open/copy fallback sheet · copy-link · Zalo coming-soon · check-in · ranking/challenge/shop toasts ·
  bottom-nav switching.
- **Pages:** `/`, `/detail`, `/report`, `/token`, `/community` for both `?lang=mm` and `?lang=vi`.
- **Viewports:** 390×844 (full set) + 430×932 (unlock modal).
- **Data mode:** `VITE_USE_MOCK=true`. Backend / API shape / DB: **not touched**.

## 3. Screenshots (`docs/qa_screenshots/lang_interaction_recheck/`)

Captured at **true device viewport** via a zero-dependency Chrome DevTools-Protocol driver
(`scripts/qa/lang_interaction_shots.mjs`) that clicks into each interaction state before capture:

`mm-unlock-modal-390.png` · `mm-report-after-unlock-390.png` · `mm-telegram-fallback-390.png` ·
`mm-copy-link-390.png` · `vi-unlock-modal-390.png` · `vi-report-after-unlock-390.png` ·
`vi-zalo-fallback-or-coming-soon-390.png` · `zh-regression-390.png` ·
`mm-unlock-modal-430.png` · `vi-unlock-modal-430.png`

> The "before" Chinese modal (mm) was also reproduced and screenshot-verified live in Claude Preview
> (Burmese title + Chinese body `已消耗 390 MTC 积分，完整 AI 报告已解锁` + Chinese button `继续查看报告`,
> 18 Han) prior to the fix.

## 4. Findings

### Chinese residual — source (the operator's bug)
| Source file | What leaked | Why |
|-------------|-------------|-----|
| `frontend/src/components/Modal.tsx` | button `继续查看报告` (hardcoded) | modal CTA never went through i18n |
| `frontend/src/store/useAppStore.ts` | modal **body** `已消耗 … 完整 AI 报告已解锁` / `支付成功…（演示模式）` | DetailPage rendered the **store/API `res.message`** (Chinese) as the modal body, for all locales |

Both surfaced through `DetailPage.tsx` (`handleUnlockToken` / `handleUnlockCash`). The modal **title**
was already i18n (`mtcDeductedTitle` etc.) — only the body + button leaked, which is why a static
scan that didn't open the modal missed it.

### Other interaction states — all clean (0 Han) after re-scan
- **mm:** unlock modal (Burmese), report-after-unlock, Telegram sheet (Burmese), copy-link toast,
  check-in `အမှတ်ယူအောင်မြင် +10 MTC`, ranking `အဆင့်စာရင်း မကြာမီ`.
- **vi:** unlock modal (Vietnamese), report-after-unlock, Zalo coming-soon `Zalo Sắp mở`,
  check-in `Điểm danh thành công +10 MTC`, ranking `Bảng xếp hạng sắp ra mắt`,
  challenge `Đã tham gia thử thách dự đoán miễn phí`, shop `-390 MTC ✓`.
- No VND/₫ on mm; no MMK/Ks on vi; no English long-form as core copy (only AI/MTC/VIP/team names + decorative subtitles).

### Dead code (not a live leak, left untouched)
`MatchCard.tsx` and `WinBar.tsx` defaults contain Chinese but are **not rendered** on any page
(no JSX usage; WinBar callers always pass localized labels). Flagged, not a customer leak.

## 5. Fixes (frontend only; no backend / API shape / DB)

- **i18n keys added** (`dict.ts` ZH+VI, `copy/en.ts`, `copy/mm.ts`): `unlockedBody`, `unlockFailedBody`,
  `continueToReport` — zh/vi/mm/en.
  - zh `已解锁，可直接查看完整报告` / `继续查看报告`
  - vi `Đã mở khóa, bạn có thể xem báo cáo đầy đủ.` / `Tiếp tục xem báo cáo`
  - mm `ဖွင့်ပြီးပါပြီ။ အစီရင်ခံစာအပြည့်အစုံကို ကြည့်နိုင်ပါသည်။` / `အစီရင်ခံစာ ဆက်ကြည့်ရန်`
  - en `Unlocked. You can view the full report.` / `Continue to report`
- **`Modal.tsx`** — added `okLabel` prop; removed hardcoded `继续查看报告`.
- **`DetailPage.tsx`** — modal **body & button are now locale-driven** (`t.unlockedBody` / `t.unlockFailedBody`
  / `t.continueToReport`); the raw `res.message` (which may be Chinese) is **no longer displayed**;
  failure toast uses `t.unlockFailedBody`.
- **`useAppStore.ts`** — hardcoded Chinese result messages replaced with neutral internal codes
  (`insufficient_mtc`, `report_unlocked_mtc`, `report_unlocked_cash_demo`) — never user-displayed.
- **Telegram fallback hint** aligned to operator "copy then paste" wording (mm & vi):
  - mm `မဖွင့်နိုင်ပါက link ကို copy လုပ်ပြီး Telegram app သို့မဟုတ် browser ထဲတွင် paste လုပ်ပါ။`
  - vi `Nếu không mở được, hãy sao chép liên kết rồi dán vào Telegram hoặc trình duyệt.`

### Telegram fallback status (ruling honored)
The active-channel open/copy sheet already exists (`CommunityPage.tsx`): **card visible · click opens
sheet · Open Telegram button · Copy Link button · hint to paste into Telegram/browser**, all locale-driven,
using the API `public_url` (still tracks `click_social_channel`). Direct-open is **accepted as PASS WITH
ISSUES**; **Copy Link is the operating primary path** and is verified working (toast surfaces the URL when
the clipboard API is unavailable). _(To screenshot the sheet in mock mode, the Telegram fallback channel
was temporarily marked active in `CommunityPage.tsx`; that edit was **reverted** after capture — verified
clean in the final diff.)_

## 6. Verification

- **mm interaction path:** unlock modal Burmese (0 Han, button no overflow @390/430); report-after-unlock
  Burmese; Telegram sheet Burmese; copy-link surfaces the t.me URL; check-in/ranking toasts Burmese.
- **vi interaction path:** unlock modal Vietnamese; Zalo coming-soon Vietnamese; check-in/ranking/challenge/shop
  toasts Vietnamese; report-after-unlock Vietnamese.
- **zh regression:** unlock modal correct Chinese (`已扣减 390 MTC 积分` / `已解锁，可直接查看完整报告` /
  `继续查看报告`) — internal management locale unaffected.
- **Price isolation:** zh RMB (`元`) · vi VND (`₫`) · mm MMK (`Ks`); no cross-leak.
- **Build:** `tsc -b && vite build` ✅ (122ms), no console errors.
- **Backend / API shape / DB:** unchanged. No bot, no payment, no scaling.

## 7. Verdict

**PASS WITH ISSUES.** The operator-reported Chinese unlock modal is fixed and every interaction state
(modal/sheet/toast) across mm & vi is now localized and screenshot-verified. Outstanding (non-engineering,
accepted): **Telegram direct-open may fail in some mobile WebViews — Copy Link is the accepted operating
path**; Vietnam Zalo remains pending active.

> Rule honored: **no screenshot, no PASS.** Evidence in `docs/qa_screenshots/lang_interaction_recheck/`.
