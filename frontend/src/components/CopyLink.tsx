import { useState } from 'react';
import type { Locale } from '../i18n/useLocale';
import { shareLink } from '../growth/shareTemplates';

// MVP2-P3 — lightweight copy/share entry (Owner: "no complex new share system required").
// Copies the ref-compatible absolute detail URL (shareTemplates.shareLink appends ?ref=).
// Pure clipboard mechanism + flash; the visible label is supplied by the call site so each
// surface keeps its own honest wording (复制情报链接 / 复制观察链接 …). No betting words here.
export function CopyLink({ path, loc, label, doneLabel, full = false }:
  { path: string; loc: Locale; label: string; doneLabel: string; full?: boolean }) {
  const [done, setDone] = useState(false);
  async function copy() {
    const url = shareLink(path, loc);
    try {
      await navigator.clipboard.writeText(url);
    } catch { /* http / WebView fallback */
      const ta = document.createElement('textarea');
      ta.value = url; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); document.body.removeChild(ta);
    }
    setDone(true); setTimeout(() => setDone(false), 1500);
  }
  return (
    <button className={full ? 'recap-cta-btn alt' : 'btn-mini'} onClick={copy}>
      🔗 {done ? doneLabel : label}
    </button>
  );
}
