import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import { prematchShareCopy, recapShareCopy, joinShareCopy, shareLink, refFor } from '../growth/shareTemplates';
import { recordJoinIntent } from '../growth/refCapture';

// Growth P1.1 — lightweight share block (Owner §2). Buttons are stage chrome;
// the copied text comes from shareTemplates (LLM judgement lines + Owner framing).
// The visitor's stored ref is preserved; otherwise the per-language operator
// default code is used. No QR here — QR lives on /share/* and the admin page.
const SB = {
  zh: { link: '复制情报链', copy: '复制分享文案', card: '查看分享卡', join: '加入情报群', done: '已复制 ✓' },
  vi: { link: 'Sao chép link', copy: 'Sao chép bài chia sẻ', card: 'Xem thẻ chia sẻ', join: 'Vào nhóm tin báo', done: 'Đã sao chép ✓' },
  my: { link: 'Link ကူးရန်', copy: 'စာသား ကူးရန်', card: 'Share card ကြည့်ရန်', join: 'အဖွဲ့ဝင်ရန်', done: 'ကူးပြီး ✓' },
};

export type ShareKind = 'prematch' | 'recap' | 'join';

function copyFor(kind: ShareKind, fixtureId: string | undefined, loc: Locale): string | null {
  if (kind === 'prematch' && fixtureId) return prematchShareCopy(fixtureId, loc);
  if (kind === 'recap' && fixtureId) return recapShareCopy(fixtureId, loc);
  if (kind === 'join') return joinShareCopy(loc);
  return null;
}

function pathFor(kind: ShareKind, fixtureId?: string): string {
  if (kind === 'prematch' && fixtureId) return `/predict/${fixtureId}`;
  if (kind === 'recap' && fixtureId) return `/recap/${fixtureId}`;
  return '/join';
}

export function ShareBlock({ kind, fixtureId, loc }: { kind: ShareKind; fixtureId?: string; loc: Locale }) {
  const navigate = useNavigate();
  const [flash, setFlash] = useState('');
  const L = loc === 'zh' ? SB.zh : loc === 'vi' ? SB.vi : loc === 'my' ? SB.my : null;
  if (!L) return null;
  const text = copyFor(kind, fixtureId, loc);
  const link = shareLink(pathFor(kind, fixtureId), loc);

  async function clip(s: string, label: string) {
    try { await navigator.clipboard.writeText(s); } catch { /* http fallback */
      const ta = document.createElement('textarea');
      ta.value = s; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); document.body.removeChild(ta);
    }
    setFlash(label); setTimeout(() => setFlash(''), 1500);
  }

  const cardTo = kind === 'recap' && fixtureId ? `/share/recap/${fixtureId}?ref=${refFor(loc)}`
    : fixtureId ? `/share/fixture/${fixtureId}?ref=${refFor(loc)}` : null;

  return (
    <div className="share-block">
      <button className="btn-mini" onClick={() => void clip(link, L.link)}>🔗 {flash === L.link ? L.done : L.link}</button>
      {text && <button className="btn-mini" onClick={() => void clip(text, L.copy)}>📋 {flash === L.copy ? L.done : L.copy}</button>}
      {cardTo && <button className="btn-mini" onClick={() => navigate(cardTo)}>🖼️ {L.card}</button>}
      <button className="btn-mini" onClick={() => { recordJoinIntent(pathFor(kind, fixtureId), loc); navigate('/join'); }}>👥 {L.join}</button>
    </div>
  );
}
