import { useNavigate, useParams } from 'react-router-dom';
import { useLocale } from '../i18n/useLocale';
import { getProductNarrative, predictSlugToId } from '../data/productNarrativeData';
import { ProductPredictView } from '../components/ProductProofViews';

// 2026 pre-match modeling product page (/predict/:slug). The main view is the
// guard-passed LLM narrative — engineering renders the stage only. zh/vi only for
// this proof; en/mm show a neutral placeholder (no engineering-template narrative).
const BARS = {
  zh: { back: '赛前建模', banner: '🔮 2026 World Cup · 赛前建模样例', none: '该样例暂未提供此语言版本' },
  vi: { back: 'Mô hình hóa trước trận', banner: '🔮 World Cup 2026 · Mẫu mô hình hóa trước trận', none: 'Mẫu này chưa có bản ngôn ngữ hiện tại' },
  en: { back: 'Pre-match modeling', banner: '🔮 2026 World Cup · pre-match modeling sample', none: 'This sample is not available in the current language yet' },
};

export function PredictPage() {
  const navigate = useNavigate();
  const loc = useLocale();
  const { slug = '2026-brazil-argentina' } = useParams();
  const B = loc === 'zh' ? BARS.zh : loc === 'vi' ? BARS.vi : BARS.en;
  const n = getProductNarrative(predictSlugToId(slug), loc);

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">{B.back}</span>
      </div>
      <div className="recap-banner">{B.banner}</div>
      {n ? (
        <ProductPredictView n={n} loc={loc} />
      ) : (
        <div className="status-card"><div className="ic">🔮</div><div className="st">{B.none}</div></div>
      )}
    </div>
  );
}
