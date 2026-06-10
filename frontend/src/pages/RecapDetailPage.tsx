import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useLocale, type Locale } from '../i18n/useLocale';
import { api } from '../api/client';
import { getBundledRecap, type RecapContent } from '../data/recapData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// Section labels (chrome). vi/mm fall back to English (never Chinese).
const LABELS: Record<'zh' | 'vi' | 'en', Record<string, string>> = {
  zh: {
    back: '历史复盘', replay: '模型回放', actual: '实际结果', conclusion: '复盘结论',
    sReplay: '模型回放 vs 实际结果', sMisses: '三个关键漏项', sEvidence: '真实证据卡',
    sCorrection: '下版模型修正', sNextData: '下一步接入数据', sOperator: '运营可用文案',
    sDataGaps: '数据缺口', sAi: 'AI 边界', sLedger: '数据来源 / Source Ledger（点击展开）',
  },
  vi: {
    back: 'Phục dựng lịch sử', replay: 'Mô hình phát lại', actual: 'Kết quả thực tế', conclusion: 'Kết luận phục dựng',
    sReplay: 'Mô hình phát lại vs Kết quả thực tế', sMisses: 'Ba điểm bỏ sót then chốt', sEvidence: 'Thẻ bằng chứng thật',
    sCorrection: 'Hiệu chỉnh mô hình bản sau', sNextData: 'Dữ liệu cần tích hợp tiếp', sOperator: 'Nội dung cho vận hành',
    sDataGaps: 'Khoảng trống dữ liệu', sAi: 'Giới hạn AI', sLedger: 'Nguồn dữ liệu / Source Ledger (nhấn để mở)',
  },
  en: {
    back: 'Historical recap', replay: 'Model replay', actual: 'Actual result', conclusion: 'Recap conclusion',
    sReplay: 'Model replay vs actual result', sMisses: 'Three key blind spots', sEvidence: 'Real evidence cards',
    sCorrection: 'Model correction (next version)', sNextData: 'Next data to ingest', sOperator: 'Operator-ready copy',
    sDataGaps: 'Data gaps', sAi: 'AI boundary', sLedger: 'Source Ledger (click to expand)',
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

  if (!content) {
    return (
      <div className="page-enter">
        <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">{L.back}</span></div>
        <div className="status-card"><div className="ic">🗂️</div><div className="st">—</div></div>
      </div>
    );
  }

  const c = content;
  const vClass = c.verdict === 'hit' ? 'green' : c.verdict === 'partial' ? 'amber' : 'red';

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">{L.back}</span>
      </div>

      {/* 0. badge + replay disclaimer */}
      <div className="recap-banner">🗂️ {c.badge}</div>

      {/* 1. strong headline + 2. one-liner */}
      <div className="card recap-hero">
        <h1 className="recap-headline">{c.headline}</h1>
        <p className="recap-oneliner">{c.oneLiner}</p>
      </div>

      {/* 3. model replay vs actual */}
      <div className="sec-en"><span className="zh">{L.sReplay}</span><span className="en">REPLAY vs ACTUAL</span></div>
      <div className="card">
        <div className="recap-vs">
          <div className="recap-vs-cell"><div className="l">{L.replay}</div><div className="v">{c.modelReplay}</div></div>
          <div className="recap-vs-cell"><div className="l">{L.actual}</div><div className="v">{c.actualResult}</div></div>
        </div>
        <div className="recap-verdict">
          <span className={`pillv ${vClass}`}>{c.verdictLabel}</span>
          <span className="recap-conclusion">{c.replayConclusion}</span>
        </div>
      </div>

      {/* 4. three key misses */}
      <div className="sec-en"><span className="zh">{L.sMisses}</span><span className="en">BLIND SPOTS</span></div>
      <div className="card">
        {c.keyMisses.map((m, i) => <div className="recap-miss" key={i}>✘ {m}</div>)}
      </div>

      {/* 5. real evidence cards */}
      <div className="sec-en"><span className="zh">{L.sEvidence}</span><span className="en">EVIDENCE</span></div>
      <div className="card"><div className="recap-evgrid">
        {c.evidence.map((e, i) => (
          <div className="recap-evcard" key={i}><div className="t">{e.label}</div><div className="v">{e.value}</div></div>
        ))}
      </div></div>

      {/* 6. model correction + next data */}
      <div className="sec-en"><span className="zh">{L.sCorrection}</span><span className="en">CORRECTION</span></div>
      <div className="card">
        <div className="recap-chips">{c.modelCorrection.map((m, i) => <span className="recap-chip" key={i}>{m}</span>)}</div>
        <div className="recap-sub2">{L.sNextData}</div>
        <div className="recap-chips">{c.nextData.map((m, i) => <span className="recap-chip need" key={i}>{m}</span>)}</div>
      </div>

      {/* 7. operator-ready copy */}
      <div className="sec-en"><span className="zh">{L.sOperator}</span><span className="en">OPERATOR COPY</span></div>
      <div className="card"><div className="recap-copybox">{c.operatorCopy}</div></div>

      {/* 8. data gaps */}
      <div className="sec-en"><span className="zh">{L.sDataGaps}</span><span className="en">DATA GAPS</span></div>
      <div className="card">{c.dataGaps.map((g, i) => <div className="recap-gap" key={i}>⚠ {g}</div>)}</div>

      {/* 9. AI boundary */}
      <div className="sec-en"><span className="zh">{L.sAi}</span><span className="en">AI BOUNDARY</span></div>
      <div className="card"><p className="small" style={{ color: '#3A4A60', lineHeight: 1.7 }}>{c.aiBoundary}</p></div>

      {/* 10. source ledger (collapsed; raw data kept secondary) */}
      <details className="card recap-ledger">
        <summary>{L.sLedger}</summary>
        <table className="recap-ledger-tbl"><tbody>
          {c.sourceLedger.map((r, i) => (
            <tr key={i}><td>{r.field}</td><td>{r.endpoint}</td><td>API-FOOTBALL</td></tr>
          ))}
        </tbody></table>
      </details>

      <div className="muted-note">{c.disclaimer}</div>
    </div>
  );
}
