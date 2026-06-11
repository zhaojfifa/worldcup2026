#!/usr/bin/env node
/**
 * MVP-2 VI Naming Consolidation + MY Locale Replication — QA screenshots
 * (zero-dep CDP driver, same pattern as mvp2_recap_flow_shots.mjs).
 * Temporary QA helper — NOT part of the build. Requires the Vite dev/preview
 * server in MOCK mode (default :4321).
 *
 * Captures the 10 sprint-acceptance shots (real rendered pages, no static mocks):
 * home zh/vi/my · predict 1489369 zh/vi/my · my rescore block · open language
 * selector (mobile sheet) · recap 855737 my · predict 1489371 my.
 *
 * Usage: node scripts/qa/mvp2_locale_consolidation_shots.mjs [BASE_URL]
 * Output: docs/qa_screenshots/mvp2_locale_consolidation/
 */
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const BASE = process.argv[2] || 'http://localhost:4321';
const OUT = 'docs/qa_screenshots/mvp2_locale_consolidation';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9368;

// full=true -> captureBeyondViewport (whole page); full=false -> viewport only
// (used for the scrolled rescore anchor and the open bottom-sheet selector).
const SHOTS = [
  { path: '/?lang=zh', file: 'home_zh.png', full: true },
  { path: '/?lang=vi', file: 'home_vi.png', full: true },
  { path: '/?lang=my', file: 'home_my.png', full: true },
  { path: '/predict/1489369?lang=zh', file: 'predict_1489369_zh.png', full: true },
  { path: '/predict/1489369?lang=vi', file: 'predict_1489369_vi.png', full: true },
  { path: '/predict/1489369?lang=my', file: 'predict_1489369_my.png', full: true },
  { path: '/predict/1489369?lang=my#rescore', file: 'predict_1489369_my_rescore.png', full: false, settle: 2500 },
  { path: '/?lang=my', file: 'language_selector_mobile.png', full: false, click: '.lang-trigger' },
  { path: '/recap/855737?lang=my', file: 'recap_855737_my.png', full: true },
  { path: '/predict/1489371?lang=my', file: 'predict_1489371_my.png', full: true },
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

async function run() {
  for (const { path, file, full, click, settle } of SHOTS) {
    await S('Page.navigate', { url: BASE + path });
    await sleep(settle ?? 1500);
    if (click) {
      await S('Runtime.evaluate', { expression: `document.querySelector(${JSON.stringify(click)})?.click()` });
      await sleep(500);
    }
    const { data } = await S('Page.captureScreenshot', { format: 'png', captureBeyondViewport: !!full });
    writeFileSync(`${OUT}/${file}`, Buffer.from(data, 'base64'));
    console.log('saved', `${OUT}/${file}`);
  }
}
try { await run(); } finally { ws.close(); chrome.kill(); }
console.log('done');
