import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import type { ProductNarrative } from '../data/productNarrativeData';
import { buildStrongCall } from '../growth/strongCallProjection';
import { ShareBlock } from './ShareBlock';

// Strong-judgment signal card (Product Closure P1; P1.1c-fix: renders THE canonical
// strong-call projection — identical values to /share cards, share copy and the CLI
// packages). Labels are stage chrome; every judgement string is an LLM narrative
// field or projected external-signal vocabulary, parsed/ordered by the projection.
const SC = {
  zh: {
    kicker: '⚡ 俅哥强判断', en: 'STRONG CALL',
    lean: '俅哥主看', score: '主比分', backup: '备选', risk: '冷门风险', variable: '最大变量', why: '为什么',
    extLabel: '外部预期 · 公开倾向',
    frame: '赛前看方向，临场看变量，赛后看校准',
    rescoreCta: '等开球前 30 分钟修正',
  },
  vi: {
    kicker: '⚡ Nhận định mạnh của Tiên Tri', en: 'STRONG CALL',
    lean: 'Tiên Tri chốt', score: 'Tỷ số chính', backup: 'Phương án phụ', risk: 'Rủi ro bất ngờ', variable: 'Biến số lớn nhất', why: 'Vì sao',
    extLabel: 'Kỳ vọng bên ngoài · Xu hướng công khai',
    frame: 'Trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh',
    rescoreCta: 'Chờ hiệu chỉnh 30 phút trước giờ đá',
  },
  my: {
    kicker: '⚡ Oracle ၏ ပြတ်သားသောအမြင်', en: 'STRONG CALL',
    lean: 'Oracle ပြတ်ပြတ်', score: 'အဓိကစကော', backup: 'အရန်', risk: 'Risk', variable: 'အကြီးဆုံး variable', why: 'ဘာကြောင့်',
    extLabel: 'ပြင်ပမျှော်လင့်ချက် · လူထုထင်မြင်ချက်',
    frame: 'ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်',
    rescoreCta: 'ပွဲမစခင် မိနစ် ၃၀ ပြန်တွက်ချက် စောင့်ရန်',
  },
};

export function StrongCallCard({ n, loc }: { n: ProductNarrative; loc: Locale }) {
  const navigate = useNavigate();
  const L = loc === 'zh' ? SC.zh : loc === 'vi' ? SC.vi : loc === 'my' ? SC.my : null;
  const call = L ? buildStrongCall(n.fixture_id, loc) : null;
  if (!L || !call) return null;
  return (
    <div className="card sc-card">
      <div className="sc-kicker"><span className="zh">{L.kicker}</span><span className="en">{L.en}</span></div>
      <div className="sc-row"><span className="sc-k">{L.lean}</span><span className="sc-v sc-lead">{call.main_lean}</span></div>
      {call.primary_score ? (
        <div className="sc-row"><span className="sc-k">{L.score}</span>
          <span className="sc-v"><span className="sc-primary-score">{call.primary_score}</span>
            {call.backup_scores.length > 0 && <span className="sc-backup">　{L.backup}: {call.backup_scores.join(' / ')}</span>}
          </span>
        </div>
      ) : (
        <div className="sc-row"><span className="sc-k">{L.score}</span><span className="sc-v">{call.scoreline_raw}</span></div>
      )}
      <div className="sc-row"><span className="sc-k">{L.risk}</span><span className="sc-v">{call.risk_label}</span></div>
      {call.top_variable && <div className="sc-row"><span className="sc-k">{L.variable}</span><span className="sc-v">{call.top_variable}</span></div>}
      {call.why && <div className="sc-row"><span className="sc-k">{L.why}</span><span className="sc-v">{call.why}</span></div>}
      {call.external_expectation.length > 0 && (
        <div className="sc-ext">
          <div className="sc-ext-label">🌐 {L.extLabel}</div>
          {call.external_expectation.map((x, i) => <div className="sc-ext-line" key={i}>· {x}</div>)}
        </div>
      )}
      <div className="sc-row"><span className="sc-k">⏱️ T-30</span><span className="sc-v">{call.t30_hook}</span></div>
      <div className="sc-frame">{L.frame}</div>
      <div className="pp-cta-row">
        <button className="recap-cta-btn" onClick={() => document.getElementById('live30')?.scrollIntoView({ behavior: 'smooth' })}>{L.rescoreCta} ▸</button>
        <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{call.cta_line} ▸</button>
      </div>
      <ShareBlock kind="prematch" fixtureId={n.fixture_id} loc={loc} />
    </div>
  );
}
