import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useLocale, type Locale } from '../i18n/useLocale';
import { api } from '../api/client';
import { getBundledRecap, MORE_RECAPS, type RecapContent } from '../data/recapData';
import { EVIDENCE_AVAILABLE, getBundledEvidence } from '../data/evidenceData';
import { getNarrative } from '../data/narrativeData';
import { NarrativeView } from '../components/NarrativeView';
import { getProductNarrative } from '../data/productNarrativeData';
import { buildRecapCall } from '../growth/strongCallProjection';
import { ProductRecapView } from '../components/ProductProofViews';
import { getUpcomingFixture } from '../data/upcomingFixtures';

// MVP2 flow P0: a fixture we PREDICTED whose recap is not ready yet (pre-match narrative,
// recap_ready=false) must show a SAFE post-match observation page — never empty, never a fake
// recap, never any internal auto-generation status wording.
const OBSERVATION = {
  zh: { back: '赛后观察', banner: '赛后观察', state: '比赛已结束 · 赛后校准中',
        lead: '这是我们赛前追踪的热点比赛，赛后观察已开启。',
        calib: '完整复盘尚未就绪；先看赛后需要校准的方向，就绪后这里会更新。', cta: '加入情报群看赛后观察' },
  vi: { back: 'Quan sát sau trận', banner: 'Quan sát sau trận', state: 'Trận đã kết thúc · Đang hiệu chỉnh sau trận',
        lead: 'Đây là trận điểm nóng chúng tôi theo dõi trước trận; quan sát sau trận đã mở.',
        calib: 'Phục dựng đầy đủ chưa sẵn sàng; xem trước hướng cần hiệu chỉnh, sẽ cập nhật khi sẵn sàng.', cta: 'Vào nhóm xem quan sát sau trận' },
  my: { back: 'ပွဲပြီး စောင့်ကြည့်ချက်', banner: 'ပွဲပြီး စောင့်ကြည့်ချက်', state: 'ပွဲ ပြီးဆုံးပြီ · ပွဲပြီး ပြန်ညှိနေဆဲ',
        lead: 'ဒါက ပွဲကြို ကျွန်ုပ်တို့ ခြေရာခံခဲ့သော အဓိကပွဲ; ပွဲပြီးသုံးသပ်ချက် စတင်ဖွင့်ပြီ။',
        calib: 'ပြည့်စုံသော ပြန်သုံးသပ်ချက် အသင့်မဖြစ်သေး; ပြန်ညှိရမည့် ဦးတည်ချက်ကို အရင်ကြည့်ပါ၊ အသင့်ဖြစ်ရင် ဤနေရာ update ပါမည်။', cta: 'ပွဲပြီးနောက် သုံးသပ်ချက်ကြည့်ရန် အဖွဲ့ဝင်ပါ' },
  en: { back: 'Post-match observation', banner: 'Post-match observation', state: 'Match finished · post-match calibration',
        lead: 'This is the hotspot match we tracked pre-match; post-match observation is open.',
        calib: 'The full recap is not ready yet; here is what needs calibration — this page updates when it is ready.', cta: 'Join for post-match notes' },
};

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// Main view prefers the LLM-generated narrative (DeepSeek, guard-passed). The
// hand-written recap/evidence copy is a DETERMINISTIC FALLBACK only (en/mm or no
// narrative). Model replay / MISS / correction / AI boundary stay folded.
const LABELS: Record<'zh' | 'vi' | 'my' | 'en', Record<string, string>> = {
  zh: {
    back: '历史复盘', lead: 'AI 怎么看这场', factors: '决定结果的三个因子', evidence: '真实数据支撑',
    operator: '运营可发文案', dataGaps: '下一版 AI 需关注的变量', internal: '模型回放与赛后判定（点击展开）',
    replay: '模型回放', actual: '实际结果', correction: '下版模型修正', nextData: '下一步接入数据', ai: 'AI 边界',
    ledger: '数据来源 / Source Ledger（点击展开）', more: '更多历史复盘', moreStatus: '更多复盘陆续接入',
    ctaQ: '想看今天这场的俅哥判断？', ctaBtn: '查看俅哥判断', ebLink: '查看完整证据面板 · 逐因子',
  },
  vi: {
    back: 'Phục dựng lịch sử', lead: 'Tiên Tri nhìn trận này thế nào', factors: 'Ba yếu tố quyết định kết quả', evidence: 'Dữ liệu thật hỗ trợ',
    operator: 'Nội dung cho vận hành', dataGaps: 'Biến số Tiên Tri cần theo dõi ở bản sau', internal: 'Mô hình phát lại & kết luận sau trận (nhấn để mở)',
    replay: 'Mô hình phát lại', actual: 'Kết quả thực tế', correction: 'Hiệu chỉnh mô hình bản sau', nextData: 'Dữ liệu cần tích hợp tiếp', ai: 'Giới hạn AI',
    ledger: 'Nguồn dữ liệu / Source Ledger (nhấn để mở)', more: 'Thêm phục dựng lịch sử', moreStatus: 'Thêm phục dựng sẽ sớm cập nhật',
    ctaQ: 'Muốn xem nhận định của Tiên Tri cho trận hôm nay?', ctaBtn: 'Xem nhận định Tiên Tri hôm nay', ebLink: 'Xem bảng bằng chứng đầy đủ · từng yếu tố',
  },
  // Burmese ('my') — visible labels Burmese; internal-fold labels stay English.
  my: {
    back: 'သမိုင်းပြန်ကြည့်', lead: 'Oracle ဒီပွဲကို ဘယ်လိုမြင်လဲ', factors: 'ရလဒ်ကို ဆုံးဖြတ်ခဲ့သည့် အချက် ၃ ချက်', evidence: 'တကယ့်ဒေတာ အထောက်အထား',
    operator: 'Operator-ready copy', dataGaps: 'နောက်ဗားရှင်းမှာ စောင့်ကြည့်ရမည့် အချက်များ', internal: 'Model replay & post-match verdict (expand)',
    replay: 'Model replay', actual: 'တကယ့်ရလဒ်', correction: 'Model correction (next version)', nextData: 'Next data to ingest', ai: 'AI boundary',
    ledger: 'Source Ledger (click to expand)', more: 'နောက်ထပ် သမိုင်းပြန်ကြည့်', moreStatus: 'နောက်ထပ် ပြန်ကြည့်မှုများ မကြာမီ',
    ctaQ: 'ဒီနေ့ပွဲအတွက် Oracle အမြင် ကြည့်မလား?', ctaBtn: 'Oracle အမြင် ကြည့်ရန်', ebLink: 'Evidence Board အပြည့် ကြည့်ရန် · အချက်ချင်း',
  },
  en: {
    back: 'Historical recap', lead: 'How the AI reads this match', factors: 'The three factors that decided it', evidence: 'Real supporting data',
    operator: 'Operator-ready copy', dataGaps: 'Variables to watch next', internal: 'Model replay & post-match verdict (expand)',
    replay: 'Model replay', actual: 'Actual result', correction: 'Model correction (next version)', nextData: 'Next data to ingest', ai: 'AI boundary',
    ledger: 'Source Ledger (click to expand)', more: 'More historical recaps', moreStatus: 'More recaps coming soon',
    ctaQ: 'Want the AI read on a current match?', ctaBtn: "See today's AI view", ebLink: 'Open the full Evidence Board · factor by factor',
  },
};

function labelsFor(loc: Locale) {
  return loc === 'zh' ? LABELS.zh : loc === 'vi' ? LABELS.vi : loc === 'my' ? LABELS.my : LABELS.en;
}

export function RecapDetailPage() {
  const navigate = useNavigate();
  const loc = useLocale();
  const { fixtureId = '855737' } = useParams();
  const L = labelsFor(loc);

  const [content, setContent] = useState<RecapContent | null>(() => getBundledRecap(fixtureId, loc));

  useEffect(() => {
    let alive = true;
    if (USE_MOCK) {
      setContent(getBundledRecap(fixtureId, loc));
      return;
    }
    api.getRecap(fixtureId, loc)
      .then(c => { if (alive) setContent(c); })
      .catch(() => { if (alive) setContent(getBundledRecap(fixtureId, loc)); });
    return () => { alive = false; };
  }, [fixtureId, loc]);

  // ── Preferred: LLM PRODUCT narrative (v2 contract, guard-passed) ───────────
  // Independent of the bundled recap content so newly productized fixtures
  // (979139) render even without hand-written fallback copy.
  const productNarr = getProductNarrative(fixtureId, loc);
  if (productNarr && (productNarr.mode === 'historical_recap' || productNarr.mode === 'real_recap')) {
    return (
      <div className="page-enter">
        <div className="backbar">
          <button className="bk" onClick={() => navigate('/')}>←</button>
          <span className="ti">{L.back}</span>
        </div>
        {/* label is local stage chrome — the backend recap proxy still carries pre-de-model
            copy (模型校准 badge) and must not surface on the LLM-narrative branch */}
        <div className="recap-banner">🗂️ {L.back}</div>
        {(() => { // P1.1c-fix: recap page leads with THE canonical recap projection
          const r = productNarr.mode === 'real_recap' ? buildRecapCall(fixtureId, loc) : null;
          if (!r) return null;
          const rightL = loc === 'zh' ? '赛前看对了什么' : loc === 'vi' ? 'Bắt đúng' : 'မှန်ခဲ့သည်';
          const devL = loc === 'zh' ? '比分为什么偏离' : loc === 'vi' ? 'Vì sao tỷ số lệch' : 'စကော ဘာကြောင့်လွဲ';
          return <div className="card sc-card">
            <div className="sc-row"><span className="sc-v sc-lead">{r.result_title}</span></div>
            {r.what_was_right && <div className="sc-row"><span className="sc-k">{rightL}</span><span className="sc-v">{r.what_was_right}</span></div>}
            <div className="sc-row"><span className="sc-k">{devL}</span><span className="sc-v">{r.why_deviated}</span></div>
            <div className="sc-frame" style={{ textAlign: 'left' }}>{r.calibration_line}</div>
            <div className="sc-row"><span className="sc-v" style={{ color: 'var(--blueMid)', fontWeight: 700 }}>{r.next_hook}</span></div>
          </div>;
        })()}
        <ProductRecapView n={productNarr} loc={loc} />
        {EVIDENCE_AVAILABLE.has(fixtureId) && (
          <button className="eb-entry-link" onClick={() => navigate(`/evidence/${fixtureId}`)}>🧭 {L.ebLink} ▸</button>
        )}
      </div>
    );
  }

  // P0 safe observation: predicted hotspot, recap NOT ready (pre-match narrative). Show a real
  // post-match observation page (we predicted this · calibration focus · group CTA) — not empty,
  // not a fake recap. Reached by direct/share link; the homepage never shows 查看复盘 here.
  if (productNarr || !content) {
    const O = OBSERVATION[loc === 'zh' ? 'zh' : loc === 'vi' ? 'vi' : loc === 'my' ? 'my' : 'en'];
    const fx = getUpcomingFixture(fixtureId);
    return (
      <div className="page-enter">
        <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">{O.back}</span></div>
        <div className="recap-banner">🗂️ {O.banner}</div>
        <div className="card th-frozen">
          <div className="th-badge sc-frozen-badge">{O.state}</div>
          {fx && <div className="th-teams">{fx.flagHome} {fx.home} <span className="ut-vs">vs</span> {fx.away} {fx.flagAway}</div>}
          <div className="th-meta">{O.lead}</div>
          <div className="th-meta">{O.calib}</div>
          <button className="recap-cta-btn" style={{ width: '100%', marginTop: 8 }} onClick={() => navigate('/community')}>{O.cta} ▸</button>
        </div>
      </div>
    );
  }

  const c = content;
  const narr = getNarrative(fixtureId, loc);

  // ── Preferred: LLM-generated narrative main view ──────────────────────────
  if (narr) {
    return (
      <div className="page-enter">
        <div className="backbar">
          <button className="bk" onClick={() => navigate('/')}>←</button>
          <span className="ti">{L.back}</span>
        </div>
        <div className="recap-banner">🗂️ {c.badge}</div>
        <div className="card recap-hero">
          <h1 className="recap-headline">{narr.hero_title}</h1>
          <p className="recap-oneliner">{narr.hero_subtitle}</p>
        </div>

        <NarrativeView narrative={narr} loc={loc} />

        {EVIDENCE_AVAILABLE.has(fixtureId) && (
          <button className="eb-entry-link" onClick={() => navigate(`/evidence/${fixtureId}`)}>🧭 {L.ebLink} ▸</button>
        )}

        <div className="sec-en"><span className="zh">{L.more}</span><span className="en">MORE RECAPS</span></div>
        <div className="card">
          {MORE_RECAPS.map(r => (
            <div className="recap-more-row" key={r.fixtureId}>
              <span className="recap-teams">{r.teams}</span>
              <span className="recap-more-status">{L.moreStatus}</span>
            </div>
          ))}
        </div>

        <div className="card recap-cta">
          <div className="recap-cta-q">{L.ctaQ}</div>
          <button className="recap-cta-btn" onClick={() => navigate('/')}>{narr.cta_copy || L.ctaBtn} ▸</button>
        </div>
        <div className="muted-note">{c.disclaimer}</div>
      </div>
    );
  }

  // ── Deterministic fallback (en/mm, or no narrative) ───────────────────────
  const eb = getBundledEvidence(fixtureId, loc);
  const vClass = c.verdict === 'hit' ? 'green' : c.verdict === 'partial' ? 'amber' : 'red';
  const heroTitle = eb ? eb.title : c.headline;
  const heroSub = eb ? eb.subtitle : c.oneLiner;
  const operatorCopy = eb ? eb.operatorCopy : c.operatorCopy;

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">{L.back}</span>
      </div>
      <div className="recap-banner">🗂️ {c.badge}</div>
      <div className="card recap-hero">
        <h1 className="recap-headline">{heroTitle}</h1>
        <p className="recap-oneliner">{heroSub}</p>
      </div>
      {eb && (
        <>
          <div className="eb-fs-list">
            {eb.firstCards.map(fc => (
              <div className={`eb-fs-card ${fc.key}`} key={fc.key}>
                <span className="eb-fs-label">{fc.label}</span>
                <span className="eb-fs-text">{fc.text}</span>
              </div>
            ))}
          </div>
          <div className="sec-en"><span className="zh">{L.lead}</span><span className="en">THE READ</span></div>
          <div className="card"><p className="eb-lead">{eb.customerLead}</p></div>
        </>
      )}
      <div className="sec-en"><span className="zh">{L.factors}</span><span className="en">KEY FACTORS</span></div>
      <div className="card">
        {c.keyMisses.map((m, i) => <div className="recap-keyfactor" key={i}>▸ {m}</div>)}
      </div>
      <div className="sec-en"><span className="zh">{L.evidence}</span><span className="en">EVIDENCE</span></div>
      <div className="card"><div className="recap-evgrid">
        {c.evidence.map((e, i) => (
          <div className="recap-evcard" key={i}><div className="t">{e.label}</div><div className="v">{e.value}</div></div>
        ))}
      </div></div>
      {EVIDENCE_AVAILABLE.has(fixtureId) && (
        <button className="eb-entry-link" onClick={() => navigate(`/evidence/${fixtureId}`)}>🧭 {L.ebLink} ▸</button>
      )}
      <div className="sec-en"><span className="zh">{L.dataGaps}</span><span className="en">WATCH NEXT</span></div>
      <div className="card">{c.dataGaps.map((g, i) => <div className="recap-gap" key={i}>🎯 {g}</div>)}</div>
      <div className="sec-en"><span className="zh">{L.operator}</span><span className="en">OPERATOR COPY</span></div>
      <div className="card"><div className="recap-copybox">{operatorCopy}</div></div>
      <details className="card recap-ledger eb-internal">
        <summary>{L.internal}</summary>
        <div className="recap-vs" style={{ marginTop: 10 }}>
          <div className="recap-vs-cell"><div className="l">{L.replay}</div><div className="v">{c.modelReplay}</div></div>
          <div className="recap-vs-cell"><div className="l">{L.actual}</div><div className="v">{c.actualResult}</div></div>
        </div>
        <div className="recap-verdict">
          <span className={`pillv ${vClass}`}>{c.verdictLabel}</span>
          <span className="recap-conclusion">{c.replayConclusion}</span>
        </div>
        <div className="eb-internal-sub">{L.correction}</div>
        <div className="recap-chips">{c.modelCorrection.map((m, i) => <span className="recap-chip" key={i}>{m}</span>)}</div>
        <div className="recap-sub2">{L.nextData}</div>
        <div className="recap-chips">{c.nextData.map((m, i) => <span className="recap-chip need" key={i}>{m}</span>)}</div>
        <div className="eb-internal-sub">{L.ai}</div>
        <p className="small" style={{ color: '#3A4A60', lineHeight: 1.7 }}>{c.aiBoundary}</p>
      </details>
      <details className="card recap-ledger">
        <summary>{L.ledger}</summary>
        <table className="recap-ledger-tbl"><tbody>
          {c.sourceLedger.map((r, i) => (
            <tr key={i}><td>{r.field}</td><td>{r.endpoint}</td><td>API-FOOTBALL</td></tr>
          ))}
        </tbody></table>
      </details>
      <div className="sec-en"><span className="zh">{L.more}</span><span className="en">MORE RECAPS</span></div>
      <div className="card">
        {MORE_RECAPS.map(r => (
          <div className="recap-more-row" key={r.fixtureId}>
            <span className="recap-teams">{r.teams}</span>
            <span className="recap-more-status">{L.moreStatus}</span>
          </div>
        ))}
      </div>
      <div className="card recap-cta">
        <div className="recap-cta-q">{L.ctaQ}</div>
        <button className="recap-cta-btn" onClick={() => navigate('/')}>{L.ctaBtn} ▸</button>
      </div>
      <div className="muted-note">{c.disclaimer}</div>
    </div>
  );
}
