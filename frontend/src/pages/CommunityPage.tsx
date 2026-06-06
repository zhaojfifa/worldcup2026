import { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { toast } from '../components/Toast';
import { SOCIAL_CHANNELS, CONTENT_STUDIO, STORAGE_STATUS, VI_TRIAL_COPY_READY } from '../copy/zh';
import { useCopy } from '../i18n/dict';
import { useLocale } from '../i18n/useLocale';
import { api, safeTrack } from '../api/client';
import type { ApiAssetsStatus } from '../api/client';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const CHANNEL_ICON: Record<string, string> = { zalo: '💬', telegram: '✈️', facebook: '📘', tiktok: '🎵' };

// Vietnamese descriptions for the fallback channel cards (keyed by channel id).
const CHANNEL_DESC_VI: Record<string, string> = {
  zalo: 'Sân nhà của fan Việt; đẩy thông tin AI & hiệu chỉnh sát giờ mỗi ngày — sắp mở.',
  telegram: 'Đẩy thông tin sát giờ; sau khi công bố đội hình, AI đồng bộ nhận định.',
  facebook: 'Thảo luận trận đấu & tổng kết dạng ảnh dài.',
  tiktok: 'Xem nhanh 3 trận AI mỗi ngày.',
};

interface ChannelView { key: string; ic: string; name: string; desc: string; status: string; url: string | null; }

function storageStatusText(
  s: ApiAssetsStatus | null,
  c: { storageChecking: string; storageConnected: string; storagePublicEnabled: string; storagePublicPending: string },
): string {
  if (!s) return c.storageChecking;
  if (!s.r2_configured) return c.storageChecking;
  if (s.public_base_url_set) return `${c.storageConnected} · ${c.storagePublicEnabled}`;
  return `${c.storageConnected} · ${c.storagePublicPending}`;
}

export function CommunityPage() {
  const t = useCopy();
  const vi = useLocale() === 'vi';
  const STATUS_LABEL: Record<string, string> = {
    coming_soon: t.statusComingSoon, active: t.statusActive, disabled: t.statusDisabled,
  };
  // Static fallback derived from centralized copy (used in mock mode or on API error).
  const FALLBACK_CHANNELS: ChannelView[] = SOCIAL_CHANNELS.map(c => ({
    key: c.id, ic: c.ic, name: c.name,
    desc: vi ? (CHANNEL_DESC_VI[c.id] ?? c.desc) : c.desc,
    status: 'coming_soon', url: null,
  }));
  const FLOW = [
    { ic: '🧠', title: t.flow1T, desc: t.flow1D },
    { ic: '📡', title: t.flow2T, desc: t.flow2D },
    { ic: '🔁', title: t.flow3T, desc: t.flow3D },
  ];
  const BENEFITS = [t.benefit1, t.benefit2, t.benefit3, t.benefit4, t.benefit5, t.benefit6, t.benefit7];

  const { subscribed, subscribe } = useAppStore();
  const [apiChannels, setApiChannels] = useState<ChannelView[] | null>(null);
  const [assetsStatus, setAssetsStatus] = useState<ApiAssetsStatus | null>(null);

  // Prefer live config; fall back to static on mock mode or API error.
  useEffect(() => {
    if (USE_MOCK) return;
    api.getSocialChannels()
      .then(list => {
        if (Array.isArray(list) && list.length) {
          setApiChannels(list.map(c => ({
            key: c.channel_name,
            ic: CHANNEL_ICON[c.channel_name] ?? '🔗',
            name: c.display_name,
            desc: c.description ?? '',
            status: c.status,
            url: c.public_url,
          })));
        }
      })
      .catch(() => { /* keep fallback; no white screen */ });
    api.getAssetsStatus()
      .then(s => setAssetsStatus(s))
      .catch(() => { /* keep null; show "确认中" */ });
  }, []);

  function handleChannelClick(ch: ChannelView) {
    safeTrack('click_social_channel', undefined, ch.key);
    if (ch.status === 'active' && ch.url) {
      window.open(ch.url, '_blank', 'noopener,noreferrer');
    } else {
      toast(`${ch.name} ${STATUS_LABEL[ch.status] ?? t.statusComingSoon}`);
    }
  }

  async function handleSubscribe() {
    if (subscribed) { toast(t.alreadySubscribed); return; }
    await subscribe();
    toast(t.subscribedToast);
  }

  const shownChannels = apiChannels ?? FALLBACK_CHANNELS;

  return (
    <div className="page-enter">
      <div className="backbar"><span className="ti">{t.communityBack}</span></div>

      {/* Price hero */}
      <div className="bigcard">
        <div className="hero-kicker" style={{ color: 'var(--gold)' }}>LIVE INTELLIGENCE VIP</div>
        <span className="pill" style={{ background: '#fff', color: 'var(--blue)', marginTop: 8 }}>{t.vipKicker}</span>
        <div className="val" style={{ fontSize: 42 }}>
          ¥199<span style={{ fontSize: 16, color: '#C5E0F6' }}>/{vi ? 'tháng' : '月'}</span>
        </div>
        <div className="xs" style={{ color: '#C5E0F6', marginTop: 4 }}>
          {t.vipPriceSub}
        </div>
      </div>

      {/* ── 社群情报矩阵 (Community Channels — placeholders) ───────── */}
      <div className="sec-en">
        <span className="zh">{t.communityTitle}</span>
        <span className="en">COMMUNITY CHANNELS</span>
      </div>
      <div className="channel-grid">
        {shownChannels.map(ch => (
          <div className="channel-card" key={ch.key} onClick={() => handleChannelClick(ch)}>
            <div className="ch-top">
              <span className="ch-ic">{ch.ic}</span>
              <span className="ch-name">{ch.name}</span>
              <span className="ch-status">{STATUS_LABEL[ch.status] ?? t.statusComingSoon}</span>
            </div>
            <div className="ch-desc">{ch.desc}</div>
          </div>
        ))}
      </div>

      {/* Intelligence flow */}
      <div className="sec-en">
        <span className="zh">{t.intelFlowTitle}</span>
        <span className="en">INTEL FLOW</span>
      </div>
      <div className="card">
        {FLOW.map(f => (
          <div className="flow-step" key={f.title}>
            <div className="fs-dot">{f.ic}</div>
            <div className="fs-body">
              <div className="fs-title">{f.title}</div>
              <div className="fs-desc">{f.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Benefits */}
      <div className="sec-en">
        <span className="zh">{t.benefitsTitle}</span>
        <span className="en">BENEFITS</span>
      </div>
      <div className="card" style={{ padding: 10 }}>
        {BENEFITS.map(b => (
          <div className="benefit" key={b}>
            <span style={{ color: 'var(--green)' }}>✔</span>{b}
          </div>
        ))}
      </div>

      {/* Why it's valuable */}
      <div className="sec-en">
        <span className="zh">{t.whyVipTitle}</span>
        <span className="en">WHY VIP</span>
      </div>
      <div className="card accent">
        <div className="row gap8 mb12">
          <span>⚡</span><span className="b small">{t.whyVipExample}</span>
        </div>
        <div className="row between small">
          <span style={{ color: '#3A4A60' }}>{t.whyVipHomeRate}</span>
          <span className="b">
            <span className="sub">45%</span>{' → '}
            <span style={{ color: 'var(--green)' }}>49% ▲</span>
          </span>
        </div>
        <p className="xs sub mt8">
          {t.whyVipReason}
        </p>
      </div>

      {/* ── AI 情报内容工厂 (Content Studio — placeholder) ────────── */}
      <div className="sec-en">
        <span className="zh">{t.csTitle}</span>
        <span className="en">{CONTENT_STUDIO.en}</span>
        <span style={{ marginLeft: 'auto' }} className="status-pill">{t.csStatus}</span>
      </div>
      <div className="card">
        {/* R2 storage readiness indicator */}
        <div className="storage-status-row">
          <span className="storage-label">{STORAGE_STATUS.label}</span>
          <span className={`storage-badge ${assetsStatus?.r2_configured ? 'ok' : 'pending'}`}>
            {storageStatusText(assetsStatus, t)}
          </span>
        </div>
        {/* Vietnamese trial copy readiness (operator-facing; not a language switch) */}
        <div className="storage-status-row">
          <span className="storage-label">{VI_TRIAL_COPY_READY.label}</span>
          <span className="storage-badge ok">{t.viBadge}</span>
        </div>
        <div className="studio-grid">
          {CONTENT_STUDIO.items.map((it, i) => (
            <div className="studio-item" key={it.label}>
              <span className="si-ic">{it.ic}</span>
              <span className="si-label">{[t.csItem1, t.csItem2, t.csItem3, t.csItem4, t.csItem5, t.csItem6][i] ?? it.label}</span>
            </div>
          ))}
        </div>
        <div className="studio-actions">
          {CONTENT_STUDIO.actions.map((a, i) => (
            <button className="studio-btn" key={a.label} disabled>{[t.csAction1, t.csAction2][i] ?? a.label}</button>
          ))}
        </div>
      </div>

      <button className="cta primary" onClick={handleSubscribe}>
        {subscribed ? t.subscribedLabel : t.subscribeNow}
      </button>

      <div className="compliance">{t.mtcStatement}</div>
      <div className="muted-note">
        {t.communityMutedNote}
      </div>
    </div>
  );
}
