import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useLocale, type Locale } from '../i18n/useLocale';
import { api } from '../api/client';
import { getBundledRecap, MORE_RECAPS, type RecapContent } from '../data/recapData';
import { EVIDENCE_AVAILABLE, getBundledEvidence } from '../data/evidenceData';
import { getNarrative } from '../data/narrativeData';
import { NarrativeView } from '../components/NarrativeView';
import { getProductNarrative } from '../data/productNarrativeData';
import { ProductRecapView } from '../components/ProductProofViews';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// Main view prefers the LLM-generated narrative (DeepSeek, guard-passed). The
// hand-written recap/evidence copy is a DETERMINISTIC FALLBACK only (en/mm or no
// narrative). Model replay / MISS / correction / AI boundary stay folded.
const LABELS: Record<'zh' | 'vi' | 'en', Record<string, string>> = {
  zh: {
    back: '历史复盘', lead: 'AI 怎么看这场', factors: '决定结果的三个因子', evidence: '真实数据支撑',
    operator: '运营可发文案', dataGaps: '下一版 AI 需关注的变量', internal: '模型回放与赛后判定（点击展开）',
    replay: '模型回放', actual: '实际结果', correction: '下版模型修正', nextData: '下一步接入数据', ai: 'AI 边界',
    ledger: '数据来源 / Source Ledger（点击展开）', more: '更多历史复盘', moreStatus: '数据已接入，复盘生成中',
    ctaQ: '想看今天这场的俅哥判断？', ctaBtn: '查看俅哥判断', ebLink: '查看完整证据面板 · 逐因子',
  },
  vi: {
    back: 'Phục dựng lịch sử', lead: 'AI nhìn trận này thế nào', factors: 'Ba yếu tố quyết định kết quả', evidence: 'Dữ liệu thật hỗ trợ',
    operator: 'Nội dung cho vận hành', dataGaps: 'Biến số AI cần theo dõi ở bản sau', internal: 'Mô hình phát lại & kết luận sau trận (nhấn để mở)',
    replay: 'Mô hình phát lại', actual: 'Kết quả thực tế', correction: 'Hiệu chỉnh mô hình bản sau', nextData: 'Dữ liệu cần tích hợp tiếp', ai: 'Giới hạn AI',
    ledger: 'Nguồn dữ liệu / Source Ledger (nhấn để mở)', more: 'Thêm phục dựng lịch sử', moreStatus: 'Đã có dữ liệu, đang tạo phục dựng',
    ctaQ: 'Muốn xem tin tức AI của trận hiện tại?', ctaBtn: 'Xem quan điểm AI hôm nay', ebLink: 'Xem bảng bằng chứng đầy đủ · từng yếu tố',
  },
  en: {
    back: 'Historical recap', lead: 'How the AI reads this match', factors: 'The three factors that decided it', evidence: 'Real supporting data',
    operator: 'Operator-ready copy', dataGaps: 'Variables to watch next', internal: 'Model replay & post-match verdict (expand)',
    replay: 'Model replay', actual: 'Actual result', correction: 'Model correction (next version)', nextData: 'Next data to ingest', ai: 'AI boundary',
    ledger: 'Source Ledger (click to expand)', more: 'More historical recaps', moreStatus: 'Data ingested, recap in progress',
    ctaQ: 'Want the AI read on a current match?', ctaBtn: "See today's AI view", ebLink: 'Open the full Evidence Board · factor by factor',
  },
};

function labelsFor(loc: Locale) {
  return loc === 'zh' ? LABELS.zh : loc === 'vi' ? LABELS.vi : LABELS.en;
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
  if (productNarr && productNarr.mode === 'historical_recap') {
    return (
      <div className="page-enter">
        <div className="backbar">
          <button className="bk" onClick={() => navigate('/')}>←</button>
          <span className="ti">{L.back}</span>
        </div>
        <div className="recap-banner">🗂️ {content?.badge ?? L.back}</div>
        <ProductRecapView n={productNarr} loc={loc} />
        {EVIDENCE_AVAILABLE.has(fixtureId) && (
          <button className="eb-entry-link" onClick={() => navigate(`/evidence/${fixtureId}`)}>🧭 {L.ebLink} ▸</button>
        )}
      </div>
    );
  }

  if (!content) {
    return (
      <div className="page-enter">
        <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">{L.back}</span></div>
        <div className="status-card"><div className="ic">🗂️</div><div className="st">—</div></div>
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
