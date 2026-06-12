import { useEffect, useState } from 'react';
import QRCode from 'qrcode';

// Growth P1 — operator dashboard (ADMIN-ONLY surface; x-admin-token gated, like the
// internal scout-pack preview). Customers never reach this: no nav link, token wall.
// QR preview lives HERE only (Owner rule: QR never renders on customer surfaces).
// All labels = sanctioned vocabulary: 情报官 · 邀请码 · 情报链 · 专属二维码 · 贡献值 ·
// MTC 积分 · 月度榜单 · 渠道贡献.
const BASE = (import.meta.env.VITE_API_BASE_URL as string) ?? 'http://localhost:8000';

interface Row {
  code: string; alias: string | null; lang: string; channel: string | null; status: string;
  clicks: number; join_intents: number; confirmed_joins: number;
  points_approved: number; points_pending: number;
}
interface Pending { id: number; code: string; points: number; reason: string; note: string | null; created_at: string; }
interface Intent { id: number; code: string; surface: string; lang: string; created_at: string; }
interface Dash { ambassadors: Row[]; pending_contributions: Pending[]; unconfirmed_intents: Intent[]; compliance: string; }

export function GrowthAdminPage() {
  // ?token= initializer is an OPERATOR convenience on this internal page only
  // (token then persists in sessionStorage; page has no nav entry, customers never land here)
  const [token, setToken] = useState(
    new URLSearchParams(window.location.search).get('token')
    ?? sessionStorage.getItem('growth_admin_token') ?? '');
  const [authed, setAuthed] = useState(false);
  const [dash, setDash] = useState<Dash | null>(null);
  const [err, setErr] = useState('');
  const [newCode, setNewCode] = useState('');
  const [qr, setQr] = useState<{ code: string; url: string; png: string } | null>(null);

  async function call(path: string, init?: RequestInit) {
    const r = await fetch(`${BASE}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', 'x-admin-token': token, ...(init?.headers ?? {}) },
    });
    if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
    return r.json();
  }

  async function load() {
    try {
      const d = await call('/api/v1/growth/admin/dashboard');
      setDash(d); setAuthed(true); setErr('');
      sessionStorage.setItem('growth_admin_token', token);
    } catch (e) { setErr(String(e)); setAuthed(false); }
  }

  useEffect(() => { if (token) void load(); /* eslint-disable-next-line */ }, []);
  // ?qr=CODE auto-opens the QR preview after auth (operator deep link)
  useEffect(() => {
    const q = new URLSearchParams(window.location.search).get('qr');
    if (authed && q) void showQr(q.toUpperCase());
    // eslint-disable-next-line
  }, [authed]);

  async function createCode() {
    try { await call('/api/v1/growth/admin/ambassadors', { method: 'POST', body: JSON.stringify({ code: newCode }) }); setNewCode(''); await load(); }
    catch (e) { setErr(String(e)); }
  }
  async function confirmIntent(id: number, decision: string) {
    try { await call(`/api/v1/growth/admin/intents/${id}/confirm`, { method: 'POST', body: JSON.stringify({ decision, actor: 'dashboard' }) }); await load(); }
    catch (e) { setErr(String(e)); }
  }
  async function review(id: number, decision: string) {
    const note = decision === 'rejected' ? (window.prompt('驳回原因（必填）') ?? '') : '';
    if (decision === 'rejected' && !note) return;
    try { await call(`/api/v1/growth/admin/contributions/${id}/review`, { method: 'POST', body: JSON.stringify({ decision, actor: 'dashboard', note }) }); await load(); }
    catch (e) { setErr(String(e)); }
  }
  async function showQr(code: string) {
    const url = `${window.location.origin}/join?ref=${code}`;
    const png = await QRCode.toDataURL(url, { width: 220, margin: 1 });
    setQr({ code, url, png });
  }

  if (!authed) {
    return (
      <div className="page-enter" style={{ padding: 16 }}>
        <h2>情报官运营台 · 管理入口</h2>
        <p className="small">仅运营使用（x-admin-token）。客户端不展示此页面。</p>
        <input value={token} onChange={e => setToken(e.target.value)} placeholder="x-admin-token"
               style={{ width: '100%', padding: 10, margin: '8px 0' }} />
        <button className="recap-cta-btn" onClick={load}>进入 ▸</button>
        {err && <div style={{ color: 'var(--amber)', fontSize: 12, marginTop: 8 }}>{err}</div>}
      </div>
    );
  }

  return (
    <div className="page-enter" style={{ padding: 12 }}>
      <h2>情报官运营台</h2>
      <div className="small" style={{ marginBottom: 8 }}>{dash?.compliance}</div>
      {err && <div style={{ color: 'var(--amber)', fontSize: 12 }}>{err}</div>}

      <div className="card">
        <b>新建邀请码</b>（QG-/TT-/FO- + 4–6 位）
        <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
          <input value={newCode} onChange={e => setNewCode(e.target.value.toUpperCase())} placeholder="QG-AB12" style={{ flex: 1, padding: 8 }} />
          <button className="recap-cta-btn" onClick={createCode}>创建 ▸</button>
        </div>
      </div>

      <div className="card" style={{ overflowX: 'auto' }}>
        <b>渠道贡献总览</b>
        <table style={{ width: '100%', fontSize: 12, marginTop: 6, borderCollapse: 'collapse' }}>
          <thead><tr style={{ textAlign: 'left', color: 'var(--sub)' }}>
            <th>邀请码</th><th>状态</th><th>点击</th><th>入群意向</th><th>确认入群</th><th>贡献值(已审)</th><th>待审</th><th>情报链</th>
          </tr></thead>
          <tbody>
            {dash?.ambassadors.map(a => (
              <tr key={a.code} style={{ borderTop: '1px solid var(--line)' }}>
                <td><b>{a.code}</b>{a.alias ? ` · ${a.alias}` : ''}</td>
                <td>{a.status}</td><td>{a.clicks}</td><td>{a.join_intents}</td><td>{a.confirmed_joins}</td>
                <td>{a.points_approved}</td><td>{a.points_pending}</td>
                <td><button className="btn-mini" onClick={() => void showQr(a.code)}>专属二维码 ▸</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {qr && (
        <div className="card" style={{ textAlign: 'center' }}>
          <b>专属二维码 · {qr.code}</b>
          <div><img src={qr.png} alt="QR" style={{ margin: '8px auto' }} /></div>
          <div className="small" style={{ wordBreak: 'break-all' }}>{qr.url}</div>
          <div className="small" style={{ color: 'var(--sub)' }}>仅限运营下载使用，客户页面不展示二维码。</div>
          <a className="recap-cta-btn" download={`qr_${qr.code}.png`} href={qr.png} style={{ display: 'inline-block', marginTop: 6 }}>下载 PNG ▸</a>
        </div>
      )}

      <div className="card">
        <b>入群意向 · 待人工确认（{dash?.unconfirmed_intents.length ?? 0}）</b>
        {dash?.unconfirmed_intents.map(i => (
          <div key={i.id} style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '6px 0', borderTop: '1px solid var(--line)', fontSize: 12 }}>
            <span style={{ flex: 1 }}>#{i.id} · {i.code} · {i.surface} · {i.lang} · {i.created_at.slice(0, 16)}</span>
            <button className="btn-mini" onClick={() => confirmIntent(i.id, 'confirmed')}>确认</button>
            <button className="btn-mini" onClick={() => confirmIntent(i.id, 'rejected')}>驳回</button>
          </div>
        ))}
      </div>

      <div className="card">
        <b>贡献值 · 待审核（{dash?.pending_contributions.length ?? 0}）</b>
        <div className="small" style={{ color: 'var(--sub)' }}>每笔 MTC 积分发放必须人工审核；积分不可提现、不可转让、不可交易。</div>
        {dash?.pending_contributions.map(p => (
          <div key={p.id} style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '6px 0', borderTop: '1px solid var(--line)', fontSize: 12 }}>
            <span style={{ flex: 1 }}>#{p.id} · {p.code} · {p.points} 贡献值 · {p.reason}{p.note ? ` · ${p.note}` : ''}</span>
            <button className="btn-mini" onClick={() => review(p.id, 'approved')}>批准</button>
            <button className="btn-mini" onClick={() => review(p.id, 'rejected')}>驳回</button>
          </div>
        ))}
      </div>
    </div>
  );
}
