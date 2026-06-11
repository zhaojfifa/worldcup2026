import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import type { ProductFactor, ProductNarrative } from '../data/productNarrativeData';
import { PRODUCT_RECAPS } from '../data/productNarrativeData';
import { MORE_RECAPS } from '../data/recapData';

// Renders the LLM-generated PRODUCT narrative (judgement / lean / risk / factors /
// growth copy) as the customer main view. Engineering renders the stage only — every
// sentence of football intelligence and ops copy is the model's (guard-passed).
// Section labels/buttons below are UI chrome (stage), not narrative.
const L10N = {
  zh: {
    judgement: '中文先知怎么判断', lean: 'AI 倾向', scoreline: '比分区间', risk: '风险评级',
    gotRight: '模型抓对了什么', underweighted: '模型低估了什么', decisive: '决定性因子', evidence: '数据证据',
    watchNext: '下次看类似比赛该盯什么', live30: '中文先知临场 30 分钟修正', keyFactors: '关键因子', tactical: '中文先知战术解读',
    freeFull: '免费版 vs 完整分析', joinGroup: '加入赛前情报群', today: '查看今日 AI 观点',
    internal: '模型依据 / 内部来源（点击展开）', opsKit: '运营素材（内部）', notes: '内部备注', sources: '来源映射',
    by: '本页判断与文案由模型生成', moreRecaps: '更多历史复盘', moreStatus: '数据已接入，复盘生成中',
    predictLink: '2026 赛前建模样例：Brazil vs Argentina', estBadge: '模型估计',
    recapDisclaimer: '历史回放样例，非真实赛前存档预测；历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。',
    predictDisclaimer: 'AI 数据观点，非结果承诺；历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。',
  },
  vi: {
    judgement: 'Tiên Tri Bóng Đá nhận định thế nào', lean: 'Thiên hướng AI', scoreline: 'Khoảng tỷ số', risk: 'Mức rủi ro',
    gotRight: 'Mô hình bắt đúng điều gì', underweighted: 'Mô hình đánh giá thấp điều gì', decisive: 'Yếu tố quyết định', evidence: 'Bằng chứng dữ liệu',
    watchNext: 'Trận tương tự lần sau nên nhìn gì', live30: 'Cập nhật 30 phút trước trận', keyFactors: 'Yếu tố then chốt', tactical: 'Thẻ chiến thuật Tiên Tri',
    freeFull: 'Bản miễn phí vs phân tích đầy đủ', joinGroup: 'Vào nhóm tình báo trước trận', today: 'Xem quan điểm AI hôm nay',
    internal: 'Cơ sở mô hình / nguồn nội bộ (nhấn để mở)', opsKit: 'Bộ nội dung vận hành (nội bộ)', notes: 'Ghi chú nội bộ', sources: 'Bản đồ nguồn',
    by: 'Nhận định và lời văn trên trang do mô hình tạo', moreRecaps: 'Thêm phục dựng lịch sử', moreStatus: 'Đã có dữ liệu, đang tạo phục dựng',
    predictLink: 'Mẫu mô hình hóa trước trận 2026: Brazil vs Argentina', estBadge: 'Mô hình ước tính',
    recapDisclaimer: 'Mẫu phát lại lịch sử, không phải dự đoán lưu trữ trước trận; thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.',
    predictDisclaimer: 'Quan điểm dữ liệu AI, không phải cam kết kết quả; thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.',
  },
  en: {
    judgement: 'How the Giành Cup scout reads it', lean: 'AI lean', scoreline: 'Scoreline band', risk: 'Risk level',
    gotRight: 'What the model got right', underweighted: 'What the model under-weighted', decisive: 'Decisive factors', evidence: 'Data evidence',
    watchNext: 'What to watch in a similar match', live30: 'What re-computes 30 minutes before kickoff', keyFactors: 'Key factors', tactical: 'Tactical read',
    freeFull: 'Free vs full analysis', joinGroup: 'Join the group for the full analysis', today: "See today's AI view",
    internal: 'Model basis / internal sources (expand)', opsKit: 'Operator kit (internal)', notes: 'Internal notes', sources: 'Source map',
    by: 'Judgement and copy on this page are model-generated', moreRecaps: 'More historical recaps', moreStatus: 'Data ingested, recap in progress',
    predictLink: '2026 pre-match modeling sample: Brazil vs Argentina', estBadge: 'Model estimate',
    recapDisclaimer: 'Historical-replay sample, not a real archived pre-match prediction; past performance does not represent future results — for data analysis and fan entertainment only.',
    predictDisclaimer: 'AI data view, not a promise of results; past performance does not represent future results — for data analysis and fan entertainment only.',
  },
};

export function ppLabels(loc: Locale) {
  return loc === 'zh' ? L10N.zh : loc === 'vi' ? L10N.vi : L10N.en;
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

function FactorList({ items }: { items: ProductFactor[] }) {
  return (
    <div className="card">
      {items.map((f, i) => (
        <div className="nv-signal" key={i}>
          <div className="nv-name">{f.name}</div>
          <div className="nv-text">{f.text}</div>
        </div>
      ))}
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
        <button className="recap-cta-btn" onClick={() => navigate('/')}>{L.today} ▸</button>
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

      <Sec zh={L.judgement} en="SCOUT READ" />
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

      <Sec zh={L.judgement} en="SCOUT READ" />
      <div className="card"><p className="eb-lead">{n.model_judgement}</p></div>
      <LeanRiskCards n={n} L={L} withScoreline={true} />

      {n.tactical_read && (
        <>
          <Sec zh={L.tactical} en="TACTICAL CARD" />
          <div className="card pp-tactical"><p className="eb-lead">{n.tactical_read}</p></div>
        </>
      )}

      <Sec zh={L.keyFactors} en="KEY FACTORS" />
      <FactorList items={n.risk_factors} />

      <Sec zh={L.live30} en="LIVE 30-MIN RE-SCORE" />
      <FactorList items={n.watch_next_signals} />

      <Sec zh={L.freeFull} en="FREE VS FULL" />
      <div className="card pp-lock">
        <div className="recap-copybox">{n.subscription_hook}</div>
        <div className="recap-cta-q" style={{ marginTop: 10 }}>{n.group_join_copy}</div>
        <div className="pp-cta-row">
          <button className="recap-cta-btn" onClick={() => navigate('/community')}>{L.joinGroup} ▸</button>
          <button className="recap-cta-btn alt" onClick={() => navigate('/')}>{L.today} ▸</button>
        </div>
      </div>

      <InternalFold n={n} L={L} open={opsOpen} />
      <div className="muted-note">{L.predictDisclaimer}</div>
    </>
  );
}
