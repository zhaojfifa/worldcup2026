import type { Locale } from '../i18n/useLocale';
import type { EvidenceBoardContent } from '../data/evidenceData';
import { FactorCard } from './FactorCard';
import { EvidenceCard } from './EvidenceCard';
import { NextVariablesCard } from './NextVariablesCard';
import { AiBoundaryCard } from './AiBoundaryCard';

// Evidence panel in customer product voice: the 3 decisive factors expanded,
// the rest folded, real supporting data, forward "next variables", an
// operator-ready copy block, and a collapsed INTERNAL block that retains the
// engineering + compliance truth (model replay / MISS, AI boundary, raw gaps,
// source ledger). vi/mm fall back to English labels (never Chinese).
const PANEL_LABELS = {
  zh: {
    sDecisive: '决定结果的三个因子', enDecisive: 'KEY FACTORS',
    sMore: '更多因子（点击展开）',
    sEvidence: '真实数据支撑', enEvidence: 'EVIDENCE',
    sNext: '下一版 AI 需重点补强的变量', enNext: 'NEXT FOR THE MODEL',
    sOperator: '运营可发文案', enOperator: 'OPERATOR COPY',
    impact: '赛后影响', interp: '解读', source: '来源',
    sInternal: '内部资料 / 数据来源（点击展开）',
    allowedTitle: 'AI 可解释', forbiddenTitle: 'AI 禁止',
    sMissingRaw: '真实数据缺口（内部）', derived: '派生自',
  },
  vi: {
    sDecisive: 'Ba yếu tố quyết định kết quả', enDecisive: 'KEY FACTORS',
    sMore: 'Thêm yếu tố (nhấn để mở)',
    sEvidence: 'Dữ liệu thật hỗ trợ', enEvidence: 'EVIDENCE',
    sNext: 'Biến số AI cần bổ sung ở bản sau', enNext: 'NEXT FOR THE MODEL',
    sOperator: 'Nội dung cho vận hành', enOperator: 'OPERATOR COPY',
    impact: 'Sau trận', interp: 'Diễn giải', source: 'Nguồn',
    sInternal: 'Tài liệu nội bộ / nguồn dữ liệu (nhấn để mở)',
    allowedTitle: 'AI được giải thích', forbiddenTitle: 'AI không được',
    sMissingRaw: 'Khoảng trống dữ liệu thật (nội bộ)', derived: 'Dẫn xuất từ',
  },
  en: {
    sDecisive: 'The three factors that decided it', enDecisive: 'KEY FACTORS',
    sMore: 'More factors (tap to expand)',
    sEvidence: 'Real supporting data', enEvidence: 'EVIDENCE',
    sNext: 'Variables the next model must add', enNext: 'NEXT FOR THE MODEL',
    sOperator: 'Operator-ready copy', enOperator: 'OPERATOR COPY',
    impact: 'Impact', interp: 'Read', source: 'Source',
    sInternal: 'Internal notes / data sources (tap to expand)',
    allowedTitle: 'AI may explain', forbiddenTitle: 'AI must not',
    sMissingRaw: 'Real data gaps (internal)', derived: 'Derived from',
  },
};

export function EvidenceBoard({ content: c, loc }: { content: EvidenceBoardContent; loc: Locale }) {
  const L = loc === 'zh' ? PANEL_LABELS.zh : loc === 'vi' ? PANEL_LABELS.vi : PANEL_LABELS.en;
  const fl = { impact: L.impact, interp: L.interp, source: L.source };
  const decisive = c.factors.filter(f => f.decisive);
  const context = c.factors.filter(f => !f.decisive);

  return (
    <>
      {/* the 3 decisive factors — expanded on first read */}
      <div className="sec-en"><span className="zh">{L.sDecisive}</span><span className="en">{L.enDecisive}</span></div>
      <div className="factor-list">
        {decisive.map(f => <FactorCard key={f.key} factor={f} labels={fl} />)}
      </div>

      {/* context factors — folded so the page isn't a wall of cards */}
      {context.length > 0 && (
        <details className="card eb-fold">
          <summary>{L.sMore}</summary>
          <div className="factor-list eb-fold-list">
            {context.map(f => <FactorCard key={f.key} factor={f} labels={fl} />)}
          </div>
        </details>
      )}

      {/* real supporting data */}
      <div className="sec-en"><span className="zh">{L.sEvidence}</span><span className="en">{L.enEvidence}</span></div>
      <div className="card"><div className="eb-evgrid">
        {c.evidence.map((e, i) => <EvidenceCard key={i} item={e} />)}
      </div></div>

      {/* forward variables (was "data gaps") */}
      <div className="sec-en"><span className="zh">{L.sNext}</span><span className="en">{L.enNext}</span></div>
      <NextVariablesCard items={c.nextVariables} />

      {/* operator-ready group copy */}
      <div className="sec-en"><span className="zh">{L.sOperator}</span><span className="en">{L.enOperator}</span></div>
      <div className="card"><div className="recap-copybox">{c.operatorCopy}</div></div>

      {/* INTERNAL — engineering + compliance truth, collapsed (not the main view) */}
      <details className="card recap-ledger eb-internal">
        <summary>{L.sInternal}</summary>
        <p className="eb-internal-view">{c.internalModelView}</p>
        <AiBoundaryCard
          allowed={c.aiAllowed}
          forbidden={c.aiForbidden}
          allowedTitle={L.allowedTitle}
          forbiddenTitle={L.forbiddenTitle}
        />
        <div className="eb-internal-sub">{L.sMissingRaw}</div>
        {c.missingEvidenceRaw.map((m, i) => <div className="eb-internal-line" key={i}>· {m}</div>)}
        <table className="recap-ledger-tbl"><tbody>
          {c.sourceLedger.map((r, i) => (
            <tr key={i}><td>{r.field}</td><td>{r.endpoint}</td><td>API-FOOTBALL</td></tr>
          ))}
        </tbody></table>
        <div className="eb-derived">{L.derived}: {c.derivedFrom.join(' · ')}</div>
        <p className="eb-internal-note">{c.rawNote}</p>
      </details>
    </>
  );
}
