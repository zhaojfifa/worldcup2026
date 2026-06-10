import { useCopy } from '../i18n/dict';

/**
 * Evidence Pack — shown on recap / finished matches that have no detailed model
 * report (e.g. synced WC-2022 matches: /reports/{id} → 404). It states exactly
 * what data is connected vs. what is missing, and a conservative recap note.
 *
 * Fabricates nothing: no player / coach / lineup / injury / odds / media values,
 * and no real scoreline (the customer API exposes none). All copy comes from the
 * dictionary (zh/en/vi/mm) so vi/mm stay non-Chinese.
 */
export function EvidencePack() {
  const t = useCopy();
  const have = [t.evHaveFixture, t.evHaveResult, t.evHaveProb, t.evHaveRecap];
  const miss = [t.evMissPlayers, t.evMissCoach, t.evMissLineup, t.evMissInjury, t.evMissMedia, t.evMissOdds];

  return (
    <div className="card accent-amber" style={{ marginTop: 14 }}>
      <div className="sec-en" style={{ marginTop: 0 }}>
        <span className="zh">🗂️ {t.evidencePackTitle}</span>
        <span className="en">EVIDENCE PACK</span>
      </div>
      <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75, marginTop: 6 }}>
        {t.evidencePackStatusNote}
      </p>

      <div style={{ marginTop: 12 }}>
        <div className="b small" style={{ color: 'var(--green)', marginBottom: 6 }}>✅ {t.evidencePackHaveTitle}</div>
        {have.map((x) => (
          <div className="feat" key={x} style={{ alignItems: 'flex-start' }}><span className="ck">✔</span>{x}</div>
        ))}
      </div>

      <div style={{ marginTop: 12 }}>
        <div className="b small" style={{ color: 'var(--amber)', marginBottom: 6 }}>⛔ {t.evidencePackMissTitle}</div>
        {miss.map((x) => (
          <div className="feat" key={x} style={{ alignItems: 'flex-start' }}>
            <span className="ck" style={{ color: 'var(--amber)' }}>—</span>{x}
          </div>
        ))}
      </div>

      <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--line)' }}>
        <div className="b small" style={{ marginBottom: 4 }}>🧭 {t.evidencePackNextTitle}</div>
        <p className="xs sub" style={{ lineHeight: 1.7 }}>{t.evidencePackNextNote}</p>
        <p className="xs sub" style={{ lineHeight: 1.7, marginTop: 8 }}>{t.evidencePackScoutNote}</p>
      </div>
    </div>
  );
}
