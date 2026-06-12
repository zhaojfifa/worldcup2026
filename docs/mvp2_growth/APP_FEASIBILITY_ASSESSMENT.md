# App Feasibility Assessment — Web / PWA / Native / Community-First / Hybrid

> Growth P1 sprint (2026-06-12). Question: where should the product live so that the T-30 rescore
> moment — our core differentiator — actually reaches fans? Internal note; no runtime authorized
> by this document.

## 1. Options scored

| Criterion | Web (now) | PWA | Native App | Community-first (TG/Zalo) | Hybrid (Web+PWA+TG) |
|---|---|---|---|---|---|
| T-30 notification | ✗ none | ◐ push: Android good, iOS 16.4+ limited, Zalo-webview none | ✓ full push | ✓✓ group message IS the notification | ✓✓ |
| Share-card distribution | ✓ screenshots + links | ✓ same + install prompt | ✓ native share sheet | ✓✓ forwarding is native culture | ✓✓ |
| Group conversion | ✓ one tap out to TG/Zalo | ✓ | ◐ extra hop | ✓✓ already in group | ✓✓ |
| Retention | ✗ weak (URL recall) | ◐ home-screen icon | ✓ | ✓✓ group re-engages daily | ✓ |
| Cost / build speed | ✓✓ zero (live today) | ✓ days (manifest+SW; push later) | ✗ weeks + store accounts | ✓✓ zero build, ops-heavy | ✓ days |
| Store friction | none | none | ✗ HIGH: sports-prediction apps face gambling-adjacent review (Apple 4.7/5.3 sensitivity; Google real-money policies); VN/MM store policy risk; rejection cycles | none | none |
| VN/MM/zh user behavior | ◐ | ◐ Android-heavy VN/MM suits PWA; iOS minority | ◐ install friction for a trial product | ✓✓ VN=Zalo/TG, MM=TG dominant, zh=group culture | ✓✓ |
| Operator workload | low | low | high (releases) | medium (manual sends, already SOP'd) | medium |
| Compliance surface | smallest | small | LARGEST (store review reads us as betting-adjacent) | medium (group content under our SOP) | small-medium |

## 2. Key facts driving the call
- The T-30 moment cannot be reliably pushed on the open web, and iOS PWA push is still
  permission-hostile; but a Telegram/Zalo GROUP message at T-30 has ~100% delivery to exactly the
  people who opted in. **Our retention mechanic is already community-shaped.**
- Native app review is our worst compliance exposure: a football-prediction app with
  scoreline bands + "intelligence" framing invites gambling-category scrutiny in exactly the
  markets we operate (VN/MM), for a product still in private trial. Zero upside at this scale.
- VN/MM are Android-dominant → PWA install (A2HS) covers most of the addressable trial users
  cheaply, and gives an icon + offline shell without store review.
- Everything that makes the loop work today (strong card, rescore hook, recap anchor, /join)
  is web — share links/QR (P1) compose perfectly with groups.

## 3. Recommendation
- **Now (this trial window):** Community-first + Web. Telegram/Zalo group = notification +
  retention layer; web = product surface; P1 /join + ref links/QR = the bridge. No store risk,
  zero build cost, operator SOP already written.
- **Next 30 days:** PWA-lite — manifest + service worker + A2HS prompt on /join and /predict
  (small, additive); evaluate Android web-push for T-30 as an OPTIONAL channel behind Owner GO
  (never auto-send; push content = the same guard-passed reminder_message). Also evaluate a
  Telegram Mini App shell (runs inside TG, no store, native-feeling) as the cheapest "app".
- **After first full fixture-cycle trial (data in hand):** revisit native ONLY if retention
  evidence shows group+PWA ceiling AND compliance counsel clears store positioning. Native is a
  scaling decision, not a trial decision.

**Verdict: HYBRID (Community-first now · PWA-lite next · native deferred until post-trial
evidence + Owner GO).**
