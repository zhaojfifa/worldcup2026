import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import type { ProductFactor, ProductNarrative } from '../data/productNarrativeData';
import { PRODUCT_RECAPS } from '../data/productNarrativeData';
import { getRescore } from '../data/rescoreData';
import { MORE_RECAPS } from '../data/recapData';

// Renders the LLM-generated PRODUCT narrative (judgement / lean / risk / factors /
// growth copy) as the customer main view. Engineering renders the stage only — every
// sentence of football intelligence and ops copy is the model's (guard-passed).
// Section labels/buttons below are UI chrome (stage), not narrative.
const L10N = {
  zh: {
    judgement: '俅哥怎么判断', lean: '俅哥倾向', scoreline: '赛前参考区间', risk: '冷门风险',
    gotRight: '俅哥赛前抓对了什么', underweighted: '俅哥当时低估了什么', decisive: '决定性因子', evidence: '数据证据',
    watchNext: '下次看类似比赛该盯什么', live30: '俅哥临场 30 分钟修正', keyFactors: '关键因子', tactical: '俅哥战术解读',
    freeFull: '免费版 vs 群内完整版', joinGroup: '加入赛前情报群', today: '查看俅哥判断', live30cta: '查看临场修正逻辑', moreVars: '更多变量', freeTier: '免费版', fullTier: '群内完整版', rsBadge: '开球前 30 分钟重算', rsRules: '俅哥的修正规则（示例）', rsWait: '加入赛前情报群，等俅哥临场修正', rsNow: '现在俅哥怎么看', rsVars: '哪三个变量会改判断', rsWhat: '开球前 30 分钟会重算什么', rsGroupQs: ['首发出来后是否改倾向', '门将/锋线是否改变风险', '比分区间是否收窄', '是否从「偏热」改为「观望/高风险」', '群内第一时间推送修正版'], freeItems: ['主倾向与风险评级', '关键变量（部分）', '战术解读方向'], fullItems: ['全部变量逐条拆解', '开球前 30 分钟首发重算', '比分区间深度解析'],
    internal: '模型依据 / 内部来源（点击展开）', opsKit: '运营素材（内部）', notes: '内部备注', sources: '来源映射',
    by: '本页判断与文案由模型生成', moreRecaps: '更多历史复盘', moreStatus: '更多复盘陆续接入',
    predictLink: '2026 赛前建模样例：Brazil vs Argentina', estBadge: '参考',
    recapDisclaimer: '历史回放样例，非真实赛前存档预测；历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。',
    predictDisclaimer: 'AI 数据观点，非结果承诺；历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。',
  },
  vi: {
    judgement: 'Tiên Tri nhận định thế nào', lean: 'Thiên hướng Tiên Tri', scoreline: 'Khoảng tham khảo trước trận', risk: 'Rủi ro bất ngờ',
    gotRight: 'Tiên Tri bắt đúng điều gì', underweighted: 'Tiên Tri từng đánh giá thấp điều gì', decisive: 'Yếu tố quyết định', evidence: 'Bằng chứng dữ liệu',
    watchNext: 'Trận tương tự lần sau nên nhìn gì', live30: 'Cập nhật 30 phút trước trận của Tiên Tri', keyFactors: 'Yếu tố then chốt', tactical: 'Thẻ chiến thuật Tiên Tri',
    freeFull: 'Bản miễn phí vs phân tích đầy đủ', joinGroup: 'Vào nhóm tin báo trước trận', today: 'Xem nhận định Tiên Tri Bóng Đá', live30cta: 'Xem cập nhật 30 phút trước trận', moreVars: 'Thêm biến số', freeTier: 'Bản miễn phí', fullTier: 'Bản đầy đủ (trong nhóm)', rsBadge: 'Tính lại 30 phút trước giờ bóng lăn', rsRules: 'Quy tắc hiệu chỉnh của Tiên Tri (ví dụ)', rsWait: 'Vào nhóm tin báo, chờ Tiên Tri hiệu chỉnh sát giờ', rsNow: 'Hiện Tiên Tri nhìn thế nào', rsVars: 'Ba biến số nào sẽ đổi nhận định', rsWhat: 'Tính lại gì 30 phút trước giờ bóng lăn', rsGroupQs: ['Đội hình ra rồi có đổi thiên hướng không', 'Thủ môn/hàng công có đổi mức rủi ro không', 'Khoảng tỷ số có thu hẹp không', 'Có chuyển từ "nghiêng cửa thắng" sang "quan sát/rủi ro cao" không', 'Bản hiệu chỉnh được đẩy trong nhóm sớm nhất'], freeItems: ['Thiên hướng chính và mức rủi ro', 'Một phần biến số then chốt', 'Hướng đọc chiến thuật'], fullItems: ['Bóc tách đủ mọi biến số', 'Tính lại 30 phút trước giờ bóng lăn theo đội hình', 'Phân tích sâu khoảng tỷ số'],
    internal: 'Cơ sở mô hình / nguồn nội bộ (nhấn để mở)', opsKit: 'Bộ nội dung vận hành (nội bộ)', notes: 'Ghi chú nội bộ', sources: 'Bản đồ nguồn',
    by: 'Nhận định và lời văn trên trang do mô hình tạo', moreRecaps: 'Thêm phục dựng lịch sử', moreStatus: 'Thêm phục dựng sẽ sớm cập nhật',
    predictLink: 'Trận mẫu trước trận 2026: Brazil vs Argentina', estBadge: 'Tham khảo',
    recapDisclaimer: 'Mẫu phát lại lịch sử, không phải dự đoán lưu trữ trước trận; thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.',
    predictDisclaimer: 'Quan điểm dữ liệu AI, không phải cam kết kết quả; thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.',
  },
  // Burmese ('my') — persona = Football Oracle (temporary trial name; Burmese
  // persona name pending Owner — docs/MVP2_MYANMAR_PERSONA_NAMING_OPTIONS.md).
  // Internal-fold labels stay English (technical zone); visible labels Burmese.
  my: {
    judgement: 'Football Oracle ဘယ်လိုမြင်လဲ', lean: 'Oracle ယိမ်းသည့်ဘက်', scoreline: 'ပွဲကြို ရည်ညွှန်းအပိုင်းအခြား', risk: 'အံ့အားသင့် အန္တရာယ်',
    gotRight: 'Oracle ပွဲကြို ဘာမှန်ခဲ့လဲ', underweighted: 'Oracle ဘာကို လျှော့တွက်ခဲ့လဲ', decisive: 'အဆုံးအဖြတ် အချက်များ', evidence: 'ဒေတာ အထောက်အထား',
    watchNext: 'နောက်တူညီပွဲမှာ ဘာစောင့်ကြည့်မလဲ', live30: 'ပွဲမစခင် မိနစ် ၃၀ Oracle ပြန်တွက်ချက်', keyFactors: 'အဓိက အချက်များ', tactical: 'Oracle နည်းဗျူဟာ ကတ်',
    freeFull: 'အခမဲ့ vs အဖွဲ့တွင်း အပြည့်အစုံ', joinGroup: 'ပွဲကြိုသတင်း အဖွဲ့ ဝင်ရန်', today: 'Oracle အမြင် ကြည့်ရန်', live30cta: 'မိနစ် ၃၀ ပြန်တွက်ချက် ကြည့်ရန်', moreVars: 'နောက်ထပ် အချက်များ', freeTier: 'အခမဲ့', fullTier: 'အဖွဲ့တွင်း အပြည့်အစုံ', rsBadge: 'ပွဲမစခင် မိနစ် ၃၀ ပြန်တွက်', rsRules: 'Oracle ၏ ပြင်ဆင်စည်းမျဉ်း (ဥပမာ)', rsWait: 'အဖွဲ့ဝင်ပြီး Oracle ၏ နောက်ဆုံးပြန်တွက်ချက် စောင့်ပါ', rsNow: 'အခု Oracle ဘယ်လိုမြင်လဲ', rsVars: 'ဘယ်အချက် ၃ ချက်က အမြင်ပြောင်းနိုင်လဲ', rsWhat: 'ပွဲမစခင် မိနစ် ၃၀ မှာ ဘာပြန်တွက်မလဲ', rsGroupQs: ['လူစာရင်းထွက်ပြီးနောက် အမြင်ပြောင်းမလား', 'ဂိုးသမား/တိုက်စစ်ကြောင့် အန္တရာယ်အဆင့် ပြောင်းမလား', 'ရမှတ်အပိုင်းအခြား ကျဉ်းသွားမလား', '"နိုင်ဘက်ယိမ်း" မှ "စောင့်ကြည့်/အန္တရာယ်မြင့်" သို့ ပြောင်းမလား', 'ပြင်ဆင်ချက်ကို အဖွဲ့ထဲမှာ အရင်ဆုံး ရမည်'], freeItems: ['အဓိက အမြင်နှင့် အန္တရာယ်အဆင့်', 'အဓိက အချက် တစ်စိတ်တစ်ပိုင်း', 'နည်းဗျူဟာ ဖတ်ရှုမှု ဦးတည်ချက်'], fullItems: ['အချက်အားလုံး တစ်ခုချင်း ခွဲပြ', 'လူစာရင်းထွက်ပြီး မိနစ် ၃၀ အတွင်း ပြန်တွက်', 'ရမှတ်အပိုင်းအခြား နက်ရှိုင်းခွဲခြမ်း'],
    internal: 'Model basis / internal sources (expand)', opsKit: 'Operator kit (internal)', notes: 'Internal notes', sources: 'Source map',
    by: 'Judgement and copy on this page are model-generated', moreRecaps: 'နောက်ထပ် သမိုင်းပြန်ကြည့်', moreStatus: 'နောက်ထပ် ပြန်ကြည့်မှုများ မကြာမီ',
    predictLink: '2026 ပွဲကြို နမူနာ: Brazil vs Argentina', estBadge: 'ရည်ညွှန်း',
    recapDisclaimer: 'သမိုင်းပြန်ကြည့် နမူနာသာဖြစ်ပြီး တကယ့်ပွဲကြို မှတ်တမ်းတင် ခန့်မှန်းချက် မဟုတ်ပါ။ အတိတ်စွမ်းဆောင်ရည်သည် အနာဂတ်ရလဒ်ကို အာမမခံပါ — ဒေတာခွဲခြမ်းစိတ်ဖြာမှုနှင့် ပရိသတ်ဖျော်ဖြေရေးအတွက်သာ။',
    predictDisclaimer: 'ဒေတာအမြင်သာဖြစ်ပြီး ရလဒ်ကတိ မဟုတ်ပါ။ အတိတ်စွမ်းဆောင်ရည်သည် အနာဂတ်ရလဒ်ကို အာမမခံပါ — ဒေတာခွဲခြမ်းစိတ်ဖြာမှုနှင့် ပရိသတ်ဖျော်ဖြေရေးအတွက်သာ။',
  },
  en: {
    judgement: 'How the Giành Cup scout reads it', lean: 'AI lean', scoreline: 'Scoreline band', risk: 'Risk level',
    gotRight: 'What the model got right', underweighted: 'What the model under-weighted', decisive: 'Decisive factors', evidence: 'Data evidence',
    watchNext: 'What to watch in a similar match', live30: 'What re-computes 30 minutes before kickoff', keyFactors: 'Key factors', tactical: 'Tactical read',
    freeFull: 'Free vs full analysis', joinGroup: 'Join the group for the full analysis', today: 'See the scout call', live30cta: 'See the 30-min re-score logic', moreVars: 'More variables', freeTier: 'Free', fullTier: 'Full (in group)', rsBadge: 'Re-scored 30 min before kickoff', rsRules: 'Re-score rules (examples)', rsWait: 'Join the group for the live re-score', rsNow: 'The current call', rsVars: 'Three variables that can change it', rsWhat: 'What re-computes 30 min before kickoff', rsGroupQs: ['Does the XI change the lean', 'Do GK/frontline change the risk', 'Does the scoreline band tighten', 'Hot pick or wait-and-see', 'Re-scored update pushed in the group first'], freeItems: ['Main lean and risk level', 'Part of the key variables', 'Tactical direction'], fullItems: ['Every variable unpacked', '30-min pre-kickoff re-score on the XI', 'Scoreline band deep-dive'],
    internal: 'Model basis / internal sources (expand)', opsKit: 'Operator kit (internal)', notes: 'Internal notes', sources: 'Source map',
    by: 'Judgement and copy on this page are model-generated', moreRecaps: 'More historical recaps', moreStatus: 'More recaps coming soon',
    predictLink: '2026 pre-match modeling sample: Brazil vs Argentina', estBadge: 'Reference',
    recapDisclaimer: 'Historical-replay sample, not a real archived pre-match prediction; past performance does not represent future results — for data analysis and fan entertainment only.',
    predictDisclaimer: 'AI data view, not a promise of results; past performance does not represent future results — for data analysis and fan entertainment only.',
  },
};

export function ppLabels(loc: Locale) {
  return loc === 'zh' ? L10N.zh : loc === 'vi' ? L10N.vi : loc === 'my' ? L10N.my : L10N.en;
}

const RECAP_TEAMS: Record<string, string> = {
  '855737': 'Argentina 1–2 Saudi Arabia · WC2022',
  '979139': 'Argentina 3–3 France · WC2022 Final',
};

function riskClass(text: string): string {
  const t = text.toLowerCase();
  if (/高|cao|high/.test(t) && !/不高|không cao/.test(t)) return 'red';
  if (/低|thấp|low/.test(t)) return 'green';
  return 'amber';
}

function FactorRow({ f }: { f: ProductFactor }) {
  return (
    <div className="nv-signal">
      <div className="nv-name">{f.name}</div>
      <div className="nv-text">{f.text}</div>
    </div>
  );
}

function FactorList({ items, top, moreLabel }: { items: ProductFactor[]; top?: number; moreLabel?: string }) {
  const head = top ? items.slice(0, top) : items;
  const rest = top ? items.slice(top) : [];
  return (
    <div className="card">
      {head.map((f, i) => <FactorRow f={f} key={i} />)}
      {rest.length > 0 && (
        <details className="pp-morevars">
          <summary>{moreLabel ?? 'More'} ({rest.length})</summary>
          {rest.map((f, i) => <FactorRow f={f} key={i} />)}
        </details>
      )}
    </div>
  );
}

function Sec({ zh, en }: { zh: string; en: string }) {
  return <div className="sec-en"><span className="zh">{zh}</span><span className="en">{en}</span></div>;
}

function LeanRiskCards({ n, L, withScoreline }: { n: ProductNarrative; L: ReturnType<typeof ppLabels>; withScoreline: boolean }) {
  return (
    <div className="card">
      <div className="pp-row"><span className="pp-k">{L.lean}</span><span className="pp-v">{n.main_lean}</span></div>
      {withScoreline && (
        <div className="pp-row">
          <span className="pp-k">{L.scoreline} <span className="recap-chip">{L.estBadge}</span></span>
          <span className="pp-v">{n.scoreline_view}</span>
        </div>
      )}
      <div className="pp-row">
        <span className="pp-k">{L.risk}</span>
        <span className="pp-v"><span className={`pillv ${riskClass(n.risk_level)}`}>{n.risk_level}</span></span>
      </div>
    </div>
  );
}

function InternalFold({ n, L, open }: { n: ProductNarrative; L: ReturnType<typeof ppLabels>; open?: boolean }) {
  return (
    <details className="card recap-ledger eb-internal" open={open}>
      <summary>{L.internal}</summary>
      <div className="eb-internal-sub">{L.notes}</div>
      {n.internal_notes.map((x, i) => <div className="eb-internal-line" key={i}>· {x}</div>)}
      <div className="eb-internal-sub">{L.opsKit}</div>
      <div className="pp-ops"><b>short_title</b> {n.short_title}</div>
      <div className="pp-ops"><b>screenshot_line</b> {n.screenshot_line}</div>
      <div className="pp-ops"><b>operator_copy</b> {n.operator_copy}</div>
      <div className="pp-ops"><b>social_post</b> {n.social_post}</div>
      <div className="eb-internal-sub">{L.sources}</div>
      <pre className="pp-srcmap">{JSON.stringify(n.source_ref_map, null, 1)}</pre>
      <div className="nv-prov">{L.by}: {n.llm_provider}{n.model ? ' · ' + n.model : ''}</div>
    </details>
  );
}

function MoreAndToday({ n, L, currentId }: { n: ProductNarrative; L: ReturnType<typeof ppLabels>; currentId: string }) {
  const navigate = useNavigate();
  const others = Array.from(PRODUCT_RECAPS).filter(id => id !== currentId);
  const pending = MORE_RECAPS.filter(r => !PRODUCT_RECAPS.has(r.fixtureId));
  return (
    <>
      <Sec zh={L.moreRecaps} en="MORE RECAPS" />
      <div className="card">
        {others.map(id => (
          <button className="pp-linkrow" key={id} onClick={() => navigate(`/recap/${id}`)}>
            <span className="recap-teams">{RECAP_TEAMS[id]}</span><span className="pp-arrow">▸</span>
          </button>
        ))}
        <button className="pp-linkrow accent" onClick={() => navigate('/predict/2026-brazil-argentina')}>
          <span className="recap-teams">{L.predictLink}</span><span className="pp-arrow">▸</span>
        </button>
        {pending.map(r => (
          <div className="recap-more-row" key={r.fixtureId}>
            <span className="recap-teams">{r.teams}</span>
            <span className="recap-more-status">{L.moreStatus}</span>
          </div>
        ))}
      </div>
      <div className="card recap-cta">
        <div className="recap-cta-q">{n.today_cta}</div>
        <button className="recap-cta-btn" onClick={() => navigate('/predict/1489369')}>{L.today} ▸</button>
      </div>
    </>
  );
}

/** Historical recap product view — structure per MVP2_LLM_DRIVEN_PRODUCT_PROOF_PLAN §5. */
export function ProductRecapView({ n, loc }: { n: ProductNarrative; loc: Locale }) {
  const navigate = useNavigate();
  const L = ppLabels(loc);
  return (
    <>
      <div className="card recap-hero">
        <h1 className="recap-headline">{n.hero_title}</h1>
        <p className="recap-oneliner">{n.hero_subtitle}</p>
      </div>

      <Sec zh={L.judgement} en="PRE-MATCH READ" />
      <div className="card"><p className="eb-lead">{n.model_judgement}</p></div>
      <LeanRiskCards n={n} L={L} withScoreline={true} />

      <Sec zh={L.gotRight} en="VALIDATED" />
      <FactorList items={n.validated_factors} />

      <Sec zh={L.underweighted} en="UNDER-WEIGHTED" />
      <FactorList items={n.underweighted_factors} />

      <Sec zh={L.decisive} en="DECISIVE FACTORS" />
      <FactorList items={n.risk_factors} />

      <Sec zh={L.evidence} en="EVIDENCE" />
      <div className="card pp-quote">“{n.screenshot_line}”</div>

      <Sec zh={L.watchNext} en="WATCH NEXT" />
      <FactorList items={n.watch_next_signals} />

      <div className="card recap-cta">
        <div className="recap-cta-q">{n.group_join_copy}</div>
        <button className="recap-cta-btn" onClick={() => navigate('/community')}>{L.joinGroup} ▸</button>
      </div>

      <MoreAndToday n={n} L={L} currentId={n.fixture_id} />
      <InternalFold n={n} L={L} />
      <div className="muted-note">{L.recapDisclaimer}</div>
    </>
  );
}

/** 30-Min ReScore product block (QiuGe sprint): free = 3 triggers; group = full list + rules. */
function RescoreBlock({ fixtureId, loc, L }: { fixtureId: string; loc: Locale; L: ReturnType<typeof ppLabels> }) {
  const navigate = useNavigate();
  const rs = getRescore(fixtureId, loc);
  if (!rs) return null;
  const free = rs.rescore_triggers.slice(0, 3);
  const locked = rs.rescore_triggers.slice(3);
  return (
    <>
      <div id="rescore" />
      <Sec zh={L.live30} en="30-MIN RE-SCORE" />
      <div className="card">
        <div className="rs-sub">{L.rsNow}</div>
        <div className="rs-head">
          <span className="recap-chip">{L.rsBadge}</span>
          <span className="rs-teaser">{rs.public_teaser}</span>
        </div>
        <div className="rs-sub">{L.rsVars}</div>
        {free.map((t, i) => (
          <div className="nv-signal" key={i}>
            <div className="nv-name">{t.name} <span className="rs-status">{t.current_status}</span></div>
            <div className="nv-text">{t.free_copy}</div>
            <div className="rs-impact">→ {t.possible_impact}</div>
          </div>
        ))}
        <div className="rs-sub">{L.rsWhat}</div>
        <div className="nv-text">{rs.pre_match_lean} · {rs.score_range_before}</div>
      </div>
      <div className="card pp-lock">
        <div className="pp-tier-h">{L.fullTier}</div>
        <div className="rs-qs">
          {L.rsGroupQs.map((q, i) => <div className="rs-q" key={i}>✓ {q}</div>)}
        </div>
        {locked.map((t, i) => (
          <div className="nv-signal" key={i}>
            <div className="nv-name">{t.name}</div>
            <div className="nv-text">{t.subscriber_copy}</div>
          </div>
        ))}
        <div className="eb-internal-sub" style={{ marginTop: 10 }}>{L.rsRules}</div>
        {rs.rescore_decision_rules.slice(0, 2).map((r, i) => (
          <div className="rs-rule" key={i}>
            <b>{r.condition}</b> → {r.change_to_lean} · {r.change_to_risk} · {r.change_to_score_range}
          </div>
        ))}
        <div className="recap-cta-q" style={{ marginTop: 10 }}>{rs.group_join_hook}</div>
        <button className="recap-cta-btn" style={{ width: '100%' }} onClick={() => navigate('/community')}>{L.rsWait} ▸</button>
      </div>
    </>
  );
}

/** 2026 pre-match modeling product view — structure per plan §5 (predict). */
export function ProductPredictView({ n, loc, opsOpen }: { n: ProductNarrative; loc: Locale; opsOpen?: boolean }) {
  const navigate = useNavigate();
  const L = ppLabels(loc);
  return (
    <>
      <div className="card recap-hero pp-predict-hero">
        <h1 className="recap-headline">{n.hero_title}</h1>
        <p className="recap-oneliner">{n.hero_subtitle}</p>
      </div>

      <Sec zh={L.judgement} en="PRE-MATCH READ" />
      <div className="card"><p className="eb-lead">{n.model_judgement}</p></div>
      <LeanRiskCards n={n} L={L} withScoreline={true} />

      {n.tactical_read && (
        <>
          <Sec zh={L.tactical} en="TACTICAL CARD" />
          <div className="card pp-tactical"><p className="eb-lead">{n.tactical_read}</p></div>
        </>
      )}

      <Sec zh={L.keyFactors} en="KEY FACTORS" />
      <FactorList items={n.risk_factors} top={3} moreLabel={L.moreVars} />

      <div id="live30" />
      {getRescore(n.fixture_id, loc) ? (
        <RescoreBlock fixtureId={n.fixture_id} loc={loc} L={L} />
      ) : (
        <>
          <Sec zh={L.live30} en="LIVE 30-MIN RE-SCORE" />
          <FactorList items={n.watch_next_signals} />
        </>
      )}

      <Sec zh={L.freeFull} en="FREE VS FULL" />
      <div className="card pp-lock">
        <div className="pp-tiers">
          <div className="pp-tier">
            <div className="pp-tier-h">{L.freeTier}</div>
            {L.freeItems.map((x, i) => <div className="pp-tier-i" key={i}>· {x}</div>)}
          </div>
          <div className="pp-tier full">
            <div className="pp-tier-h">{L.fullTier}</div>
            {L.fullItems.map((x, i) => <div className="pp-tier-i" key={i}>· {x}</div>)}
          </div>
        </div>
        <div className="recap-copybox">{n.subscription_hook}</div>
        <div className="recap-cta-q" style={{ marginTop: 10 }}>{n.group_join_copy}</div>
        <div className="pp-cta-row">
          <button className="recap-cta-btn" onClick={() => navigate('/community')}>{L.joinGroup} ▸</button>
          <button className="recap-cta-btn alt" onClick={() => document.getElementById('live30')?.scrollIntoView({ behavior: 'smooth' })}>{L.live30cta} ▸</button>
        </div>
      </div>

      <InternalFold n={n} L={L} open={opsOpen} />
      <div className="muted-note">{L.predictDisclaimer}</div>
    </>
  );
}
