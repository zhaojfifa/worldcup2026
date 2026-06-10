#!/usr/bin/env node
/**
 * MVP-2 Scout Pack operator-preview QA screenshots (zero-dep CDP driver).
 * Temporary QA helper — NOT part of the production build. Requires the backend
 * running (default :8099) with ingested samples present.
 *
 * Full-page captures of the internal operator preview (/internal/scout-pack)
 * for zh + vi, fixtures 855737 (Argentina vs Saudi Arabia) and 855741
 * (Germany vs Japan).
 *
 * Usage: node scripts/qa/mvp2_scout_pack_shots.mjs [BASE_URL]
 * Output: docs/qa_screenshots/mvp2_real_data_operator_review/
 */
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const BASE = process.argv[2] || 'http://localhost:8099';
const OUT = 'docs/qa_screenshots/mvp2_real_data_operator_review';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9355;
const SHOTS = [
  { lang: 'zh', fid: '855737' },
  { lang: 'vi', fid: '855737' },
  { lang: 'zh', fid: '855741' },
  { lang: 'vi', fid: '855741' },
];
mkdirSync(OUT, { recursive: true });

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=/tmp/qa-chrome-${PORT}`, 'about:blank',
], { stdio: 'ignore' });

async function getWsUrl() {
  for (let i = 0; i < 50; i++) {
    try { const r = await fetch(`http://localhost:${PORT}/json/version`); const j = await r.json(); if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl; } catch {}
    await sleep(200);
  }
  throw new Error('Chrome CDP did not come up');
}
function cdp(ws) {
  let id = 0; const pending = new Map();
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
  const send = (method, params = {}, sessionId) => new Promise((res, rej) => { const mid = ++id; pending.set(mid, (m) => m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result)); ws.send(JSON.stringify({ id: mid, method, params, sessionId })); });
  return { send };
}
const ws = await (async () => { const url = await getWsUrl(); const sock = new WebSocket(url); await new Promise((res, rej) => { sock.addEventListener('open', res); sock.addEventListener('error', rej); }); return sock; })();
const { send } = cdp(ws);
const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
const S = (m, p) => send(m, p, sessionId);
await S('Page.enable'); await S('Runtime.enable');
await S('Emulation.setDeviceMetricsOverride', { width: 1200, height: 1000, deviceScaleFactor: 2, mobile: false });

async function nav(url) { await S('Page.navigate', { url }); await sleep(700); }
async function shot(file) {
  const { data } = await S('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  writeFileSync(`${OUT}/${file}`, Buffer.from(data, 'base64'));
  console.log('saved', `${OUT}/${file}`);
}

async function run() {
  for (const { lang, fid } of SHOTS) {
    await nav(`${BASE}/internal/scout-pack?fixture_id=${fid}&lang=${lang}`);
    await shot(`${lang}_${fid}_scout_pack.png`);
  }
}
try { await run(); } finally { ws.close(); chrome.kill(); }
console.log('done');
