# MVP-2 — Evidence Board v2 Operator Real-Device Review (Checklist + Package)

> **Phase:** MVP-2 Evidence Board v2 **Operator Real-Device Review** · **Date:** 2026-06-10 ·
> **Branch / commit:** `feature/mvp2-api-football-ingestion` @ `d838bf5` (PR #3, **Draft**) ·
> **Mode:** internal verification (mock / `VITE_USE_MOCK=true`, operation **paused**, `public_ready=false`).
> **Subject:** the minimal Evidence Board v2 implementation
> ([MVP2_USER_REVIEW_REPORT_EVIDENCE_BOARD_V2](MVP2_USER_REVIEW_REPORT_EVIDENCE_BOARD_V2.md), engineer review = PASS WITH ISSUES).
>
> **This is a review-support document.** It contains NO runtime/frontend/backend change. It is for an operator
> to run the real-device pass and record a verdict. **Implementation is frozen this phase** (see §0).

---

## 0. Owner ruling (2026-06-10) — review only, do NOT develop
冻结(本阶段一律不做):
```text
不再扩功能 · 不 mark PR #3 ready · 不 merge
不新增 homepage EBv2 entry · 不建 backend evidence proxy
不产品化 979139 · 不接 TheSports · 不验证 live DeepSeek / Gemini
不接付费 / Token · 不恢复运营
```
本阶段允许:更新 review 文档 · 整理访问 URL / 截图路径 · 记录 operator feedback。
本阶段禁止:runtime code · frontend change · backend change · new sample · new vendor · new LLM · PR ready。

---

## 1. Review package (access) — 整理给 operator
| 项目 | 值 |
|---|---|
| Live frontend (现网) | https://worldcup2026-izid.onrender.com — **注意:部署自 `main`;当前 EBv2 仅在 Draft 分支(未合并),现网 `/evidence` 暂不存在。** |
| Live backend | https://worldcup2026-api-71n6.onrender.com（EBv2 为 bundled,前端不依赖后端即可渲染） |
| Branch / commit | `feature/mvp2-api-football-ingestion` @ `d838bf5`（PR #3, Draft, 未合并） |
| 真机交互运行(推荐) | `frontend/.env.local` 已含 `VITE_USE_MOCK=true`(本地、gitignored)→ 根目录 `npm run dev -- --host` → 手机同 Wi-Fi 访问 `http://<电脑局域网IP>:5173`；或纯本机 `npm run dev` → `http://localhost:5173` |
| Recap path (zh) | `/recap/855737?lang=zh` |
| Recap path (vi) | `/recap/855737?lang=vi` |
| Evidence path (zh) | `/evidence/855737?lang=zh` |
| Evidence path (vi) | `/evidence/855737?lang=vi` |
| zh 截图 | `docs/qa_screenshots/mvp2_evidence_board_v2/evidence_855737_zh.png` · `recap_855737_zh_eb_entry.png` |
| vi 截图 | `docs/qa_screenshots/mvp2_evidence_board_v2/evidence_855737_vi.png` · `recap_855737_vi_eb_entry.png` |

> **真机复核两种方式:** (A) 直接在手机查看上面 4 张全页截图(390×844 @2x,视觉忠实,无需环境);
> (B) 本地 mock 运行做交互复核(返回 / 折叠 / 语言切换)。无现网部署 = 这是当前的已知约束(见 §9-4)。

---

## 2. 验证对象 (subjects)
- [ ] `/recap/855737` — zh
- [ ] `/recap/855737` — vi
- [ ] `/evidence/855737` — zh
- [ ] `/evidence/855737` — vi

## 3. 验证路径 (paths)
- [ ] 首页 → 「历史复盘 · World Cup 2022」→ Argentina vs Saudi Arabia → `/recap/855737`
- [ ] 复盘详情 → 「查看完整证据面板 · 逐因子 ▸」→ `/evidence/855737`
- [ ] Evidence Board → 「查看历史复盘」返回复盘(back ← 也回到复盘页,不死胡同)
- [ ] Evidence Board → 「查看今日 AI 观点」回首页(无付费 / 无 Token)

---

## 4. 普通用户检查项 (ordinary fan)
| # | 检查项 | zh | vi |
|---|---|---|---|
| 4.1 | 是否一眼看懂 AI 倾向(Argentina · 历史回放 · 信心档位 低 ★★☆☆☆,无百分比)? | [ ] | [ ] |
| 4.2 | 是否理解 **MISS 不是失败宣传,而是模型问责**(敢认错 → 升级样本)? | [ ] | [ ] |
| 4.3 | 是否看懂 **7 个因子卡**(来源 / 影响 / 解读 + 「假设」标记)? | [ ] | [ ] |
| 4.4 | 是否看懂 **真实证据卡**(69%/31% · 15/3 · 6/2 · 6.0/7.7 · 0/5)? | [ ] | [ ] |
| 4.5 | 是否知道 **数据缺口**(伤停 P0 / xG / 近期状态)且未被掩盖? | [ ] | [ ] |

## 5. 运营检查项 (operator)
| # | 检查项 | 结论 |
|---|---|---|
| 5.1 | 哪些区域适合截图?(预期:hero 强标题 / AI 倾向+MISS / 决定性因子卡 / 证据卡) | ______ |
| 5.2 | 标题是否可传播(「证据面板 · 这场爆冷里 ScoutScore 的判断、盲区与缺口」)? | [ ] 是 / [ ] 否 |
| 5.3 | **因子卡是否太密**(7 张一次铺开)? | [ ] 合适 / [ ] 偏密 |
| 5.4 | 是否需要**折叠非决定性因子**(仅展开 决定性 / 漏判)? | [ ] 需要 / [ ] 不需要 |
| 5.5 | 是否适合发群(自带历史回放声明 + 免责声明)? | [ ] 是 / [ ] 否 |
| 5.6 | **zh 是否自然**(无翻译腔 / 无残留)? | [ ] 是 / [ ] 否 |
| 5.7 | **vi 是否自然**(母语顺,无生硬)? | [ ] 是 / [ ] 否 |

## 6. 付费前用户检查项 (pre-paid)
| # | 检查项 | 结论 |
|---|---|---|
| 6.1 | 是否觉得比普通 AI 文案**更专业 / 有方法论**(因子级 + 来源级透明)? | [ ] 是 / [ ] 否 |
| 6.2 | 是否愿意继续看「今日 AI 观点」(continuation 是否成立)? | [ ] 是 / [ ] 否 |
| 6.3 | 是否**还缺 CTA**(把"证据可信"转化为"想看更多")? | [ ] 缺 / [ ] 够 |
| 6.4 | 是否希望看**更多复盘**(更多样例)? | [ ] 是 / [ ] 否 |

## 7. 合规检查项 (compliance — 全部应为"是/通过")
| # | 检查项 | zh | vi |
|---|---|---|---|
| 7.1 | **vi Han = 0**(整页含顶栏 0 汉字;工程已测 body Han=0) | n/a | [ ] |
| 7.2 | 无 betting / odds / 盘口 / 竞猜 / 投注 | [ ] | [ ] |
| 7.3 | 无百分比胜率 / 命中率(信心仅档位 + 星级) | [ ] | [ ] |
| 7.4 | 无 fake archived prediction(满屏「历史回放 · 非真实赛前存档预测」) | [ ] | [ ] |
| 7.5 | 无 xG / SHAP / injuries inference(伤停标「source required」,绝不写"无伤停") | [ ] | [ ] |
| 7.6 | 无付费 / Token 流;continuation 仅回首页 / 复盘 | [ ] | [ ] |

---

## 8. Operator verdict (待 operator 填写)
```text
operator_name:        ____________________
device / viewport:    ____________________ (e.g. iPhone 13, 390x844 / Android)
review_method:        [ ] 截图  [ ] 本地 mock 真机  [ ] 两者
date:                 ____________________

verdict:              [ ] PASS
                      [ ] PASS WITH ISSUES
                      [ ] FAIL
                      [ ] BLOCKED

blocker (if BLOCKED): ____________________________________________
```
**Operator feedback (自由记录,按视角):**
- 普通用户: ____________________________________________
- 运营:     ____________________________________________
- 付费前:   ____________________________________________
- 合规:     ____________________________________________

**Owner final decision (待 Owner 记录):** ____________________________________________

---

## 9. Current known issues (来自 engineer User Review v2,供 operator 参考)
1. **因子卡密度偏高**(7 张)——普通球迷可能只读前 2–3 张;候选改进:决定性因子优先 / 非决定性折叠(**本阶段冻结,仅记录**)。
2. **仅复盘页入口、仅 855737**——首页 EBv2 入口、第二样例(979139)为后续 Owner 决策(**本阶段冻结**)。
3. **后端 `GET /api/v1/evidence/{id}` 未建**——当前 bundled-only;真实部署前需补 proxy(**本阶段冻结**)。
4. **EBv2 未部署到 live Render**——在 Draft 分支(未合并)、运营暂停 → 真机复核经本地 mock 或已提交截图(**约束,非缺陷**)。
5. **付费转化 CTA 留白**——continuation 不接付费流(按设计);转化钩子是后续设计题。
6. **`/injuries`(0 条)「来源」**对非技术用户略硬——可读性微调候选(**本阶段仅记录**)。

## 10. Decision options (operator verdict → Owner 下一步,均需单独 GO)
| verdict | 含义 | Owner 下一步候选(本阶段不执行) |
|---|---|---|
| **PASS** | 内部验收通过(仍 mock / 运营暂停) | 记录 `final_owner_decision`;EBv2 minimal 定稿;再议是否进入下一增量 |
| **PASS WITH ISSUES** | 成立但有打磨点 | 把 §9 候选分流:折叠非决定性因子 / homepage 入口 / 979139 / backend proxy / 付费 CTA 设计——逐项单独 GO |
| **FAIL** | 表达 / 合规不达标 | 回到 design,不 ship;记录失败原因 |
| **BLOCKED** | 无法完成真机复核 | 记录 blocker(如需 PR preview 部署 / 真机访问受限)+ 解锁条件 |

---

## Guardrails honored (this doc)
review-support only · 无 runtime / frontend / backend change · 仅新增本 review 文档 · 未改首页预测主逻辑 ·
未 mark PR #3 ready · 未 merge · 未新增 homepage 入口 / backend proxy / 979139 / TheSports / live LLM ·
未接付费 / Token · 运营暂停 · `public_ready=false` · vi Han=0 规则 · PR #2 未动 · PR #3 Draft。
