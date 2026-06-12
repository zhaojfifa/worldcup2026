import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import type { ProductNarrative } from '../data/productNarrativeData';
import { getExternalSignals } from '../data/externalSignalData';
import { ShareBlock } from './ShareBlock';

// Strong-judgment signal card (Product Closure P1, Owner §7).
// Labels are engineering stage chrome; EVERY judgement string rendered here is an
// LLM narrative field (main_lean / scoreline_view / risk_level / factor names) or
// the script-projected customer-safe external-signal vocabulary. Engineering
// writes no football narrative.
const SC = {
  zh: {
    kicker: '⚡ 俅哥强判断', en: 'STRONG CALL',
    lean: '俅哥主看', score: '赛前参考比分', risk: '冷门风险', variable: '最大变量',
    frame: '赛前看方向，临场看变量，赛后看校准',
    rescoreCta: '等开球前 30 分钟修正', groupCta: '进群看完整版',
  },
  vi: {
    kicker: '⚡ Nhận định mạnh của Tiên Tri', en: 'STRONG CALL',
    lean: 'Tiên Tri nghiêng về', score: 'Tỷ số tham khảo trước trận', risk: 'Rủi ro bất ngờ', variable: 'Biến số lớn nhất',
    frame: 'Trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh',
    rescoreCta: 'Chờ hiệu chỉnh 30 phút trước giờ đá', groupCta: 'Vào nhóm xem bản đầy đủ',
  },
  my: {
    kicker: '⚡ Oracle ၏ ပြတ်သားသောအမြင်', en: 'STRONG CALL',
    lean: 'Oracle ဦးတည်ချက်', score: 'ပွဲကြို ရည်ညွှန်းစကော', risk: 'အံ့အားသင့်နိုင်ခြေ', variable: 'အကြီးဆုံး variable',
    frame: 'ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်',
    rescoreCta: 'ပွဲမစခင် မိနစ် ၃၀ ပြန်တွက်ချက် စောင့်ရန်', groupCta: 'အဖွဲ့ထဲ ဗားရှင်းအပြည့် ကြည့်ရန်',
  },
};

export function StrongCallCard({ n, loc }: { n: ProductNarrative; loc: Locale }) {
  const navigate = useNavigate();
  const L = loc === 'zh' ? SC.zh : loc === 'vi' ? SC.vi : loc === 'my' ? SC.my : null;
  if (!L) return null;
  const topVariable = n.watch_next_signals?.[0]?.name || n.risk_factors?.[0]?.name || '';
  const ext = getExternalSignals(n.fixture_id, loc);
  return (
    <div className="card sc-card">
      <div className="sc-kicker"><span className="zh">{L.kicker}</span><span className="en">{L.en}</span></div>
      <div className="sc-row"><span className="sc-k">{L.lean}</span><span className="sc-v sc-lead">{n.main_lean}</span></div>
      <div className="sc-row"><span className="sc-k">{L.score}</span><span className="sc-v">{n.scoreline_view}</span></div>
      <div className="sc-row"><span className="sc-k">{L.risk}</span><span className="sc-v">{n.risk_level}</span></div>
      {topVariable && <div className="sc-row"><span className="sc-k">{L.variable}</span><span className="sc-v">{topVariable}</span></div>}
      {ext && (
        <div className="sc-ext">
          <div className="sc-ext-label">🌐 {ext.label}</div>
          {ext.lines.map((x, i) => <div className="sc-ext-line" key={i}>· {x}</div>)}
        </div>
      )}
      <div className="sc-frame">{L.frame}</div>
      <div className="pp-cta-row">
        <button className="recap-cta-btn" onClick={() => document.getElementById('live30')?.scrollIntoView({ behavior: 'smooth' })}>{L.rescoreCta} ▸</button>
        <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{L.groupCta} ▸</button>
      </div>
      <ShareBlock kind="prematch" fixtureId={n.fixture_id} loc={loc} />
    </div>
  );
}
