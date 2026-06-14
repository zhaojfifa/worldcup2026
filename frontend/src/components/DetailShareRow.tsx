import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import { CopyLink } from './CopyLink';
import { recordJoinIntent } from '../growth/refCapture';

// MVP2-P3 — share/copy + join CTA row for detail pages (gate #6: prediction detail and
// recap detail both include share/copy AND a join CTA). `kind` only swaps the copy label so
// the wording is honest per surface (情报链接 for predict, 观察链接 for recap). Join records
// join-intent against the stored ref, then routes to /community. No auto-send.
const D = {
  zh: { predict: '复制情报链接 / 分享预测', recap: '复制观察链接 / 分享复盘', done: '已复制 ✓', join: '加入临场情报群' },
  vi: { predict: 'Sao chép link / chia sẻ nhận định', recap: 'Sao chép link quan sát / chia sẻ', done: 'Đã sao chép ✓', join: 'Vào nhóm sát giờ' },
  my: { predict: 'Link ကူး / share', recap: 'စောင့်ကြည့် link ကူး / share', done: 'ကူးပြီး ✓', join: 'ပွဲနီး အဖွဲ့ ဝင်ရန်' },
  en: { predict: 'Copy / share prediction link', recap: 'Copy / share observation link', done: 'Copied ✓', join: 'Join the live group' },
};

export function DetailShareRow({ path, loc, kind }:
  { path: string; loc: Locale; kind: 'predict' | 'recap' }) {
  const navigate = useNavigate();
  const C = loc === 'zh' ? D.zh : loc === 'vi' ? D.vi : loc === 'my' ? D.my : D.en;
  return (
    <div className="share-block">
      <CopyLink path={path} loc={loc} label={kind === 'recap' ? C.recap : C.predict} doneLabel={C.done} />
      <button className="btn-mini" onClick={() => { recordJoinIntent(path, loc); navigate('/community'); }}>
        👥 {C.join}
      </button>
    </div>
  );
}
