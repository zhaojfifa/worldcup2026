import { useEffect, useRef, useState } from 'react';
import { useLocale, setLocale, type Locale } from '../i18n/useLocale';

/**
 * Product-grade language selector (replaces the old CN | VI | MY button row).
 *
 * One compact 🌐 control showing the CURRENT language in its own script; tapping
 * opens a menu — a bottom sheet on narrow/mobile widths, a dropdown on desktop
 * (CSS-driven, see .lang-menu in global.css). Selecting a language persists it
 * (localStorage + ?lang= URL param via setLocale) and keeps the current route.
 */
const OPTIONS: { code: Locale; native: string; tag: string }[] = [
  { code: 'zh', native: '中文', tag: 'ZH' },
  { code: 'vi', native: 'Tiếng Việt', tag: 'VI' },
  { code: 'my', native: 'မြန်မာ', tag: 'MY' },
];

export function LanguageSelector() {
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const current = OPTIONS.find((o) => o.code === locale) ?? OPTIONS[0];

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent | TouchEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onDown);
    document.addEventListener('touchstart', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('touchstart', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  const choose = (code: Locale) => {
    setLocale(code); // persists + updates ?lang=, never navigates
    setOpen(false);
  };

  return (
    <div className="lang-selector" ref={rootRef}>
      <button
        className="lang-trigger"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label="language"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="lang-globe">🌐</span>
        <span className="lang-current">{current.native}</span>
        <span className="lang-caret">▾</span>
      </button>
      {open && (
        <>
          <div className="lang-backdrop" onClick={() => setOpen(false)} />
          <div className="lang-menu" role="listbox" aria-label="language options">
            {OPTIONS.map((o) => (
              <button
                key={o.code}
                role="option"
                aria-selected={o.code === locale}
                className={`lang-option ${o.code === locale ? 'on' : ''}`}
                onClick={() => choose(o.code)}
              >
                <span className="lang-native">{o.native}</span>
                <span className="lang-tag">{o.tag}</span>
                <span className="lang-check">{o.code === locale ? '✓' : ''}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
