import { useNavigate } from 'react-router-dom';
import { useLocale } from '../i18n/useLocale';
import { recordJoinIntent } from '../growth/refCapture';
import { ShareBlock } from '../components/ShareBlock';

// Growth P1 — /join?ref=<code> ambassador landing (Owner GO 2026-06-12).
// Customer surface: persona value proposition + group CTA ONLY. No QR, no admin
// machinery, no code echo back to the visitor. The group link is operator-configured
// (VITE_GROUP_LINK_{ZH,VI,MY}); unset = CTA routes to /community (existing flow).
const J = {
  zh: {
    kicker: '俅哥带你看球', sub: '强判断足球情报室',
    frame: '赛前看方向，临场看变量，赛后看校准',
    rows: [
      { ic: '⚡', h: '赛前强判断', p: '俅哥主看、参考比分、冷门风险——开赛前就把方向讲清楚。' },
      { ic: '⏱️', h: '30 分钟临场修正', p: '首发公布后，俅哥重新看一遍：最终倾向、参考比分、冷门风险，群内更新。' },
      { ic: '🗂️', h: '赛后复盘校准', p: '方向对没对、比分差在哪，赛后逐项讲清楚——判断可追溯，不删记录。' },
    ],
    cta: '进群看临场修正 ▸', alt: '先看今天的判断 ▸',
    note: '入群免费 · 内容为数据分析与球迷娱乐参考',
  },
  vi: {
    kicker: 'Xem bóng cùng Tiên Tri Bóng Đá', sub: 'Phòng tin tức nhận định mạnh',
    frame: 'Trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh',
    rows: [
      { ic: '⚡', h: 'Nhận định mạnh trước trận', p: 'Thiên hướng, tỷ số tham khảo, rủi ro bất ngờ — rõ ràng trước giờ bóng lăn.' },
      { ic: '⏱️', h: 'Hiệu chỉnh 30 phút trước trận', p: 'Đội hình công bố xong, Tiên Tri xem lại: thiên hướng cuối, tỷ số tham khảo, rủi ro — cập nhật trong nhóm.' },
      { ic: '🗂️', h: 'Phục dựng sau trận', p: 'Đúng hướng hay không, lệch ở đâu — nói rõ từng điểm, không xoá lịch sử.' },
    ],
    cta: 'Vào nhóm xem hiệu chỉnh sát giờ ▸', alt: 'Xem nhận định hôm nay ▸',
    note: 'Vào nhóm miễn phí · Nội dung là phân tích dữ liệu, tham khảo giải trí cho người hâm mộ',
  },
  my: {
    kicker: 'Football Oracle နဲ့ ပွဲကြည့်မယ်', sub: 'ပြတ်သားအမြင် သတင်းခန်း',
    frame: 'ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်',
    rows: [
      { ic: '⚡', h: 'ပွဲကြို ပြတ်သားအမြင်', p: 'ဦးတည်ချက် · ရည်ညွှန်းစကော · risk — ပွဲမစခင် ရှင်းရှင်းလင်းလင်း။' },
      { ic: '⏱️', h: 'မိနစ် ၃၀ ပြန်တွက်ချက်', p: 'Lineup ထွက်ပြီးနောက် Oracle ပြန်ကြည့်ပြီး အဖွဲ့ထဲ နောက်ဆုံးအမြင် တင်ပေးမည်။' },
      { ic: '🗂️', h: 'ပွဲပြီး ပြန်သုံးသပ်ချက်', p: 'ဘာမှန်ခဲ့/ဘာလွဲခဲ့လဲ အချက်ချက်ရှင်းပြသည် — မှတ်တမ်းမဖျက်ပါ။' },
    ],
    cta: 'အဖွဲ့ဝင်ပြီး ပြန်တွက်ချက် ကြည့်ရန် ▸', alt: 'ဒီနေ့အမြင် ကြည့်ရန် ▸',
    note: 'အဖွဲ့ဝင်ခြင်း အခမဲ့ · ဒေတာသုံးသပ်ချက်နှင့် ပရိသတ်ဖျော်ဖြေရေး ရည်ညွှန်းချက်သာ',
  },
  en: {
    kicker: 'Watch with Giành Cup', sub: 'Strong-call football intel room',
    frame: 'Direction pre-match, variables late, calibration after',
    rows: [
      { ic: '⚡', h: 'Strong pre-match call', p: 'Lean, reference scoreline, upset risk — clear before kickoff.' },
      { ic: '⏱️', h: '30-min late re-check', p: 'Once lineups land, the final lean updates in the group.' },
      { ic: '🗂️', h: 'Honest recap', p: 'What was right, what was off — on the record.' },
    ],
    cta: 'Join the group ▸', alt: "See today's call ▸",
    note: 'Free to join · data analysis & fan-entertainment reference',
  },
};

const GROUP_LINK: Record<string, string | undefined> = {
  zh: import.meta.env.VITE_GROUP_LINK_ZH as string | undefined,
  vi: import.meta.env.VITE_GROUP_LINK_VI as string | undefined,
  my: import.meta.env.VITE_GROUP_LINK_MY as string | undefined,
};

export function JoinPage() {
  const navigate = useNavigate();
  const loc = useLocale();
  const L = loc === 'zh' ? J.zh : loc === 'vi' ? J.vi : loc === 'my' ? J.my : J.en;
  const groupLink = GROUP_LINK[loc];

  function onJoin() {
    recordJoinIntent('/join', loc);
    if (groupLink) window.open(groupLink, '_blank', 'noopener');
    else navigate('/community');
  }

  return (
    <div className="page-enter">
      <div className="card recap-hero pp-predict-hero">
        <h1 className="recap-headline">{L.kicker}</h1>
        <p className="recap-oneliner">{L.sub}</p>
        <div className="sc-frame">{L.frame}</div>
      </div>
      <div className="card">
        {L.rows.map(r => (
          <div className="join-row" key={r.h}>
            <span className="join-ic">{r.ic}</span>
            <div className="join-body">
              <div className="join-h">{r.h}</div>
              <div className="join-p">{r.p}</div>
            </div>
          </div>
        ))}
        <button className="recap-cta-btn" style={{ width: '100%', marginTop: 10 }} onClick={onJoin}>{L.cta}</button>
        <button className="recap-cta-btn alt" style={{ width: '100%', marginTop: 8 }} onClick={() => navigate('/predict/1489371')}>{L.alt}</button>
      </div>
      <div className="card"><ShareBlock kind="join" loc={loc} /></div>
      <div className="muted-note">{L.note}</div>
    </div>
  );
}
