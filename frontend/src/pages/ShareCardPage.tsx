import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import QRCode from 'qrcode';
import { useLocale } from '../i18n/useLocale';
import { getProductNarrative } from '../data/productNarrativeData';
import { getUpcomingFixture } from '../data/upcomingFixtures';
import { getExternalSignals } from '../data/externalSignalData';
import { SITE, DEFAULT_REF, splitScoreband } from '../growth/shareTemplates';

// Growth P1.1 — screenshot-friendly share card (Owner §5). This is a SHARE route,
// not a normal customer match page: QR is allowed here by Owner rule. All judgement
// strings are LLM narrative fields; labels + framing are Owner vocabulary.
const SC = {
  zh: { pre: '俅哥强判断', recap: '俅哥复盘 · 赛后看校准', lean: '俅哥主看', score: '参考比分', risk: '冷门风险',
        variable: '最大变量', hook: '开球前 30 分钟，群内更新最终倾向和比分区间', scan: '扫码进群等临场修正',
        frame: '赛前看方向，临场看变量，赛后看校准' },
  vi: { pre: 'Nhận định mạnh của Tiên Tri', recap: 'Tiên Tri phục dựng', lean: 'Nghiêng về', score: 'Tỷ số tham khảo',
        risk: 'Rủi ro bất ngờ', variable: 'Biến số lớn nhất',
        hook: 'Nhóm cập nhật thiên hướng cuối 30 phút trước giờ đá', scan: 'Quét mã vào nhóm',
        frame: 'Trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh' },
  my: { pre: 'Oracle ပြတ်သားအမြင်', recap: 'Oracle ပြန်သုံးသပ်ချက်', lean: 'ဦးတည်ချက်', score: 'ရည်ညွှန်းစကော',
        risk: 'Risk', variable: 'အဓိက variable', hook: 'ပွဲမစခင် မိနစ် ၃၀ အဖွဲ့ထဲ နောက်ဆုံးအမြင် တင်မည်',
        scan: 'Scan ဖတ်ပြီး အဖွဲ့ဝင်ရန်', frame: 'ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်' },
};

export function ShareCardPage({ kind }: { kind: 'fixture' | 'recap' }) {
  const { fixtureId = '' } = useParams();
  const [search] = useSearchParams();
  const loc = useLocale();
  const L = loc === 'vi' ? SC.vi : loc === 'my' ? SC.my : SC.zh;
  const lang = loc === 'vi' || loc === 'my' ? loc : 'zh';
  const ref = (search.get('ref') ?? DEFAULT_REF[lang]).toUpperCase();
  const n = getProductNarrative(fixtureId, lang);
  const fx = getUpcomingFixture(fixtureId);
  const [qr, setQr] = useState('');
  const joinUrl = `${SITE}/join?ref=${ref}`;

  useEffect(() => { void QRCode.toDataURL(joinUrl, { width: 132, margin: 1 }).then(setQr); }, [joinUrl]);

  if (!n) return <div className="page-enter" style={{ padding: 24 }}>—</div>;
  const isRecap = kind === 'recap' || n.mode === 'real_recap';
  const topVar = n.watch_next_signals?.[0]?.name || n.risk_factors?.[0]?.name || '';
  const ext = !isRecap ? getExternalSignals(fixtureId, lang as 'zh' | 'vi' | 'my') : null;

  return (
    <div className="share-card-page">
      <div className="share-card">
        <div className="shc-brand">Giành Cup · {lang === 'zh' ? '俅哥说球' : lang === 'vi' ? 'Tiên Tri Bóng Đá' : 'Football Oracle'}</div>
        <div className="shc-kicker">{isRecap ? L.recap : L.pre}</div>
        {fx && <div className="shc-teams">{fx.flagHome} {fx.home} <span>vs</span> {fx.away} {fx.flagAway}</div>}
        {!fx && <div className="shc-teams">{n.short_title}</div>}
        {isRecap ? (
          <>
            <div className="shc-line shc-strong">{n.short_title}</div>
            <div className="shc-line">{n.screenshot_line}</div>
          </>
        ) : (
          <>
            <div className="shc-row shc-lean"><b>{L.lean}</b><span>{n.main_lean}</span></div>
            {(() => {
              const band = splitScoreband(n.scoreline_view);
              if (!band) return <div className="shc-row"><b>{L.score}</b><span>{n.scoreline_view}</span></div>;
              return (
                <div className="shc-scoreband">
                  <span className="shc-primary">{band.primary}</span>
                  {band.alts.length > 0 && (
                    <span className="shc-alts">{lang === 'zh' ? '备选' : lang === 'vi' ? 'Phụ' : 'အရန်'}: {band.alts.join(' / ')}</span>
                  )}
                </div>
              );
            })()}
            <div className="shc-row"><b>{L.risk}</b><span>{n.risk_level}</span></div>
            {topVar && <div className="shc-row"><b>{L.variable}</b><span>{topVar}</span></div>}
            {ext && <div className="shc-ext">{ext.lines[0]}</div>}
          </>
        )}
        <div className="shc-hook">⏱️ {L.hook}</div>
        <div className="shc-foot">
          {qr && <img src={qr} alt="QR" className="shc-qr" />}
          <div className="shc-foot-txt">
            <div className="shc-scan">{L.scan}</div>
            <div className="shc-url">{joinUrl}</div>
            <div className="shc-frame">{L.frame}</div>
          </div>
        </div>
        <div className="shc-disclaimer">{lang === 'zh' ? '历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。'
          : lang === 'vi' ? 'Kết quả quá khứ không bảo đảm tương lai; chỉ là phân tích dữ liệu, tham khảo giải trí.'
            : 'အတိတ်ရလဒ်သည် အနာဂတ်ကို အာမမခံပါ — ဒေတာသုံးသပ်ချက် ရည်ညွှန်းချက်သာ။'}</div>
      </div>
    </div>
  );
}
