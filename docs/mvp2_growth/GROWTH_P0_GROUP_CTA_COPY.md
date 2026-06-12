# Growth P0 — Group CTA Copy Pack (design-only)

> Rule: every message a fan reads comes from a guard-passed LLM artifact (quoted verbatim below,
> with its source path) or is an Owner-approved fixed label. Operators replace ONLY
> [群链接由运营填写]. Hand-rewriting judgement copy = forbidden (sha256 tamper-reject backstop).

## 1. On-product CTA labels (already live, fixed set)
- Homepage: 加入情报群 ▸ · 进群等临场修正——首发公布后，俅哥重新看一遍再给最终倾向。
  vi: Vào nhóm tin báo ▸ · my: အဖွဲ့ဝင်ရန် ▸
- Predict page: 进群看完整版 ▸ / 等开球前 30 分钟修正 ▸ (vi/my equivalents live)
- Recap page: 看俅哥怎么校准 ▸ → group CTA in ProductRecapView

## 2. Group intro message (paste once when a fan joins)
Source: LLM `group_join_copy`, `docs/data_audit/mvp2_trial_prediction_narratives/1489371.{lang}.deepseek.json`
- zh:「想第一时间收到巴西vs摩洛哥的临场修正？开球前30分钟，首发一公布，俅哥在群内重新判断方向、
  比分区间和风险等级。免费版看大方向，群内看临场变数。加入俅哥说球群，不错过任何关键信号。」
- vi: “Vào nhóm Tiên Tri Bóng Đá để xem phân tích đầy đủ: nhận định chiều sâu, cập nhật sát giờ và
  thảo luận cùng người hâm mộ…” (full text in artifact)
- my: “Football Oracle ရဲ့ ပွဲကြိုအမြင်ကို လက်လွတ်မခံပါနဲ့ — အဖွဲ့ထဲမှာ ပွဲမစခင် မိနစ် ၃၀…” (full text in artifact)

## 3. T-30 reminder message (send ONLY after A3 guard_passed + approve + Owner GO)
Source: LLM `reminder_message`, `docs/data_audit/mvp2_rescore_models/1489371.{lang}.deepseek.json`
- zh:「【俅哥提醒】巴西vs摩洛哥首发已出！群内正在重算：巴西防线是否完整？摩洛哥门将是谁？
  点此查看最新判断和比分区间调整。」
- Public teaser (outside group): 「俅哥提醒：巴西vs摩洛哥，首发名单是今晚最大冷门密码，开球前30分钟见分晓。」
- vi/my: same artifact files, language versions; if a language failed guard, that language is NOT sent.

## 4. Post-recap follow-up (FT+recap approved)
Source: recap `operator_copy` + `group_join_copy`, `docs/data_audit/mvp2_send_kits/{fixture}.recap.md`.
1489369 zh example (live kit):「俅哥复盘：墨西哥2-0南非——方向对了，但比分被红牌放大。…想看临场30分钟
重算？进群看。」Follow-up framing label (fixed): 赛前看方向，临场看变量，赛后看校准——下一场见。

## 5. Send-order per fixture
pre-match (group intro / share card) → T-30 reminder (A3-gated) → kickoff = STOP all pre-match
material → FT+recap approved → recap follow-up + next-fixture hook.

## 6. Forbidden in ALL group copy
Betting/odds/handicap vocab (4 languages, even negated) · win guarantees · reward-for-invite
promises · 提现/commission/recharge wording · fabricated urgency（最后X个名额）· links inside LLM
prose (operator pastes link separately) · any copy not present in a guard-passed artifact.
