import type { Locale } from '../i18n/useLocale';
import type { EvidenceBoardContent } from '../data/evidenceData';
import { FactorCard } from './FactorCard';
import { EvidenceCard } from './EvidenceCard';
import { MissingDataCard } from './MissingDataCard';
import { AiBoundaryCard } from './AiBoundaryCard';

// Reusable Evidence Board panel: factor cards + evidence cards + missing-data +
// AI boundary, with the source ledger and raw Scout Pack kept collapsed at the
// foot. Designed to be shared by the recap page (now) and a future prediction
// detail page. vi/mm fall back to English labels (never Chinese).
const PANEL_LABELS = {
  zh: {
    sFactors: '模型因素卡', enFactors: 'FACTORS',
    sEvidence: '真实证据卡', enEvidence: 'EVIDENCE',
    sMissing: '缺失数据 / 边界', enMissing: 'MISSING DATA',
    sBoundary: 'AI 边界', enBoundary: 'AI BOUNDARY',
    source: '来源', impact: '影响', interp: '解读', assumption: '假设',
    allowedTitle: 'AI 可解释', forbiddenTitle: 'AI 禁止',
    sLedger: '数据来源 / Source Ledger（点击展开）',
    sRaw: '原始 Scout Pack（折叠）', derived: '派生自',
  },
  vi: {
    sFactors: 'Thẻ yếu tố mô hình', enFactors: 'FACTORS',
    sEvidence: 'Thẻ bằng chứng thật', enEvidence: 'EVIDENCE',
    sMissing: 'Dữ liệu còn thiếu / giới hạn', enMissing: 'MISSING DATA',
    sBoundary: 'Giới hạn AI', enBoundary: 'AI BOUNDARY',
    source: 'Nguồn', impact: 'Tác động', interp: 'Diễn giải', assumption: 'Giả định',
    allowedTitle: 'AI được giải thích', forbiddenTitle: 'AI không được',
    sLedger: 'Nguồn dữ liệu / Source Ledger (nhấn để mở)',
    sRaw: 'Scout Pack gốc (thu gọn)', derived: 'Dẫn xuất từ',
  },
  en: {
    sFactors: 'Factor cards', enFactors: 'FACTORS',
    sEvidence: 'Real evidence', enEvidence: 'EVIDENCE',
    sMissing: 'Missing data / boundary', enMissing: 'MISSING DATA',
    sBoundary: 'AI boundary', enBoundary: 'AI BOUNDARY',
    source: 'Source', impact: 'Impact', interp: 'Interpretation', assumption: 'Assumption',
    allowedTitle: 'AI may explain', forbiddenTitle: 'AI must not',
    sLedger: 'Source Ledger (click to expand)',
    sRaw: 'Raw Scout Pack (collapsed)', derived: 'Derived from',
  },
};

export function EvidenceBoard({ content: c, loc }: { content: EvidenceBoardContent; loc: Locale }) {
  const L = loc === 'zh' ? PANEL_LABELS.zh : loc === 'vi' ? PANEL_LABELS.vi : PANEL_LABELS.en;

  return (
    <>
      {/* Factor cards — the model's pre-match factors + post-match validation */}
      <div className="sec-en"><span className="zh">{L.sFactors}</span><span className="en">{L.enFactors}</span></div>
      <div className="factor-list">
        {c.factors.map(f => (
          <FactorCard
            key={f.key}
            factor={f}
            labels={{ source: L.source, impact: L.impact, interp: L.interp, assumption: L.assumption }}
          />
        ))}
      </div>

      {/* Real evidence cards (provenance-tagged) */}
      <div className="sec-en"><span className="zh">{L.sEvidence}</span><span className="en">{L.enEvidence}</span></div>
      <div className="card"><div className="eb-evgrid">
        {c.evidence.map((e, i) => <EvidenceCard key={i} item={e} />)}
      </div></div>

      {/* Missing data / honest gaps */}
      <div className="sec-en"><span className="zh">{L.sMissing}</span><span className="en">{L.enMissing}</span></div>
      <MissingDataCard items={c.missingData} />

      {/* AI boundary */}
      <div className="sec-en"><span className="zh">{L.sBoundary}</span><span className="en">{L.enBoundary}</span></div>
      <AiBoundaryCard
        allowed={c.aiAllowed}
        forbidden={c.aiForbidden}
        allowedTitle={L.allowedTitle}
        forbiddenTitle={L.forbiddenTitle}
      />

      {/* Source ledger — always present, collapsed at the foot */}
      <details className="card recap-ledger">
        <summary>{L.sLedger}</summary>
        <table className="recap-ledger-tbl"><tbody>
          {c.sourceLedger.map((r, i) => (
            <tr key={i}><td>{r.field}</td><td>{r.endpoint}</td><td>API-FOOTBALL</td></tr>
          ))}
        </tbody></table>
      </details>

      {/* Raw Scout Pack — collapsed, secondary (kept in internal preview, not dumped here) */}
      <details className="card recap-ledger">
        <summary>{L.sRaw}</summary>
        <p className="small sub" style={{ marginTop: 8, lineHeight: 1.7 }}>{c.rawNote}</p>
        <div className="eb-derived">{L.derived}: {c.derivedFrom.join(' · ')}</div>
      </details>
    </>
  );
}
