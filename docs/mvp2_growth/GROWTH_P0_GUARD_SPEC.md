# Growth P0 — Guard Spec for Share/Growth Material (design-only)

> Principle: growth material is a PROJECTION of already-guarded product surfaces. Therefore the
> primary gate is the existing pipeline (narrative guard + visible-copy scanner). This spec defines
> what must additionally hold for anything used as share material, and what a future
> `check_growth_material.py` would scan (NOT implemented in P0 — operator checklist covers it).

## 1. Forbidden — betting vocabulary (any language, even negated)
zh: 赔率 盘口 投注 博彩 下注 庄家 让球 大小球 跟单 竞猜 串关 购彩 彩票 亚盘 让球盘
vi: kèo · cửa trên · cửa dưới · nhà cái · cá cược · đặt cược · soi kèo · tài xỉu · chấp bóng
my: လောင်းကစား · လောင်းကြေး · အလောင်းအစား · လောင်းထား · ကြေးပေါက် · ပေါက်ကြေး
en: betting · odds · handicap · bookmaker · bet slip · wager · parlay

## 2. Forbidden — win-guarantee vocabulary
稳赚 稳赢 必中 必赢 包赢 跟单 · chắc thắng · bao thắng · ăn chắc · သေချာပေါက် · အာမခံ ·
guaranteed win · sure win · 命中率/胜率 as a promise (real match stats like possession % allowed)

## 3. Forbidden — commission/reward/incentive vocabulary
佣金 返佣 充值 提现(except 不可提现 in compliance footer only) 返现 奖金池 分成 拉新奖励 邀请返利 ·
hoa hồng · nạp tiền · rút tiền · commission · recharge · payout · cash reward · invite bonus ·
任何「分享得X」「邀请得X」结构 — sharing earns NOTHING in P0.

## 4. Forbidden — agent/proxy hierarchy vocabulary
代理 总代 上级/下级代理 层级 团队长 · đại lý · agent tier · sub-agent · downline ·
(my: ဒိုင် alone = referee, allowed; လောင်းဒိုင် = bookmaker, banned)

## 5. Forbidden — process/audit leakage
模型 AI(standalone) 数据缺失 缺数据 盲区 过程验证 自证 · mô hình · thiếu dữ liệu · မော်ဒယ် ·
ဒေတာမရှိ · sha256 · artifact · guard · provider · mock · missing evidence · data gap · source names

## 6. Allowed replacement language (the only sanctioned vocabulary)
俅哥判断/俅哥主看/赛前参考区间/冷门风险/临场变量/外部预期/市场共识/公开预测倾向/热度集中在热门方/
冷门变量被低估/赛前看方向，临场看变量，赛后看校准 + vi/my equivalents already live on product surfaces.

## 7. Scan requirements before share material is used
1. The SOURCE surface passed the latest live visible-copy scan (18/18) on the current deploy.
2. The pasted COPY exists verbatim in a guard-passed artifact (send-kit path recorded).
3. The card screenshot is of the live surface (not a mockup, not edited).
4. Operator eyeballs the §1–§5 lists against the final assembled message (image + text + link).
5. Any violation = DO NOT SEND; regenerate via pipeline, never hand-edit.

## 8. Future (NOT P0): `scripts/check_growth_material.py`
Would scan an assembled send bundle (text + OCR of card) against §1–§5. Requires Owner GO on a
later growth phase; P0 relies on the existing scanner + this checklist.
