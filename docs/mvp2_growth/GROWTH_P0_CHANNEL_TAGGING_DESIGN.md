# Growth P0 — Channel/Source Tagging Design (design-only, manual record)

> Goal: know which CHANNEL a send went to — never which USER. No tracking runtime, no QR
> attribution, no per-user links, no cookies/params. Tags are manual strings in operator records.

## 1. Allowed tag set (fixed; extend only via Owner approval)
| tag | meaning |
|---|---|
| `telegram_group_1` | the my-MM test group (existing t.me/GianhCupMMAIFootball scope) |
| `zalo_test_group` | vi trusted Zalo group (when active) |
| `telegram_vi_trusted` | vi trusted Telegram circle |
| `zh_internal_group` | zh internal ops group |
| `facebook_dm` | manual 1:1 DM by operator |
| `operator_manual` | anything else done by hand (note required) |

## 2. Where the tag is recorded
1. **Queue**: `mark-sent --channel <tag> --group "<human name>" --screenshot <path>` — channel
   field takes the tag verbatim (existing CLI, no code change).
2. **Operator log** (manual file `docs/data_audit/mvp2_trial_sends/SEND_LOG.md`, appended by hand):
   `| date-utc | fixture | surface | lang | tag | group name | screenshot path | Owner GO ref |`
3. **Feedback form**: each feedback entry notes the tag it came from (channel-level only).

## 3. Explicitly NOT in P0
- No `?src=` URL params, no UTM, no per-user invite codes, no QR codes, no shortlinks.
- No user-level attribution of joins; group join counts are read manually from the group UI and
  recorded as a number per tag in the weekly note.
- No runtime: no tables, no endpoints, no analytics SDK.

## 4. Weekly counting (manual)
Operator records per tag: sends, screenshots, approximate joins (group member delta), feedback
count. Counts only — no identities. Goes into the trial feedback report skeleton.
