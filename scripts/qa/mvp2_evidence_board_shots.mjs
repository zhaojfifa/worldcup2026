#!/usr/bin/env node
/**
 * MVP-2 Evidence Board v2 QA screenshots (zero-dep CDP driver).
 * Temporary QA helper — NOT part of the build. Requires the Vite dev server
 * running in MOCK mode (VITE_USE_MOCK=true, default :5173).
 *
 * Captures, full-page, for zh + vi:
 *   Evidence Board (/evidence/855737)  +  Recap page showing the new EB entry link
 *
 * Usage: node scripts/qa/mvp2_evidence_board_shots.mjs [BASE_URL]
 * Output: docs/qa_screenshots/mvp2_evidence_board_v2/
 */
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const BASE = process.argv[2] || 'http://localhost:5173';
const OUT = 'docs/qa_screenshots/mvp2_evidence_board_v2';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9367;
// Product Voice Sprint: capture the customer-voice rewrite. Earlier
// evidence_855737_{zh,vi}.png (the FAIL-for-copy version) stay committed as the
// "before" reference for the Owner Product Voice Review.
const SHOTS = [
  { path: '/evidence/855737?lang=zh', file: 'evidence_855737_zh_product_voice.png' },
  { path: '/evidence/855737?lang=vi', file: 'evidence_855737_vi_product_voice.png' },
  { path: '/recap/855737?lang=zh', file: 'recap_855737_zh_product_voice.png' },
  { path: '/recap/855737?lang=vi', file: 'recap_855737_vi_product_voice.png' },
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
await S('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });

async function nav(path) { await S('Page.navigate', { url: BASE + path }); await sleep(1500); }
async function shot(file) {
  const { data } = await S('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  writeFileSync(`${OUT}/${file}`, Buffer.from(data, 'base64'));
  console.log('saved', `${OUT}/${file}`);
}

async function run() {
  for (const { path, file } of SHOTS) { await nav(path); await shot(file); }
}
try { await run(); } finally { ws.close(); chrome.kill(); }
console.log('done');
