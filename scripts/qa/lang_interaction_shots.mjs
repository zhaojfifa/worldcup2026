#!/usr/bin/env node
/**
 * Language INTERACTION-state QA screenshots (zero-dep Chrome DevTools Protocol driver).
 * Temporary QA helper — NOT part of the production build. Requires a running dev server.
 *
 * Captures modal / action-sheet / toast states that a static page-load screenshot cannot:
 * unlock modal, report-after-unlock, Telegram open/copy fallback sheet, copy-link toast,
 * Zalo coming-soon toast — for mm & vi, plus a zh regression home shot.
 *
 * Usage: node scripts/qa/lang_interaction_shots.mjs [BASE_URL]
 * Output: docs/qa_screenshots/lang_interaction_recheck/ at true device viewport (390/430).
 *
 * NOTE: requires the temporary "QA_TELEGRAM_ACTIVE_TEMP" edit in CommunityPage.tsx so the
 * Telegram card is active in mock mode (the open/copy sheet only shows for active channels).
 * Revert that edit after running.
 */
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const BASE = process.argv[2] || 'http://localhost:5173';
const OUT = 'docs/qa_screenshots/lang_interaction_recheck';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;
mkdirSync(OUT, { recursive: true });

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=/tmp/qa-chrome-${PORT}`, 'about:blank',
], { stdio: 'ignore' });

async function getWsUrl() {
  for (let i = 0; i < 50; i++) {
    try {
      const r = await fetch(`http://localhost:${PORT}/json/version`);
      const j = await r.json();
      if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl;
    } catch { /* not up yet */ }
    await sleep(200);
  }
  throw new Error('Chrome CDP did not come up');
}

function cdp(ws) {
  let id = 0; const pending = new Map(); const sessions = new Map();
  ws.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  });
  const send = (method, params = {}, sessionId) => new Promise((res, rej) => {
    const mid = ++id;
    pending.set(mid, (m) => m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result));
    ws.send(JSON.stringify({ id: mid, method, params, sessionId }));
  });
  return { send, sessions };
}

const ws = await (async () => {
  const url = await getWsUrl();
  const sock = new WebSocket(url);
  await new Promise((res, rej) => { sock.addEventListener('open', res); sock.addEventListener('error', rej); });
  return sock;
})();

const { send } = cdp(ws);
const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
const S = (method, params) => send(method, params, sessionId);
await S('Page.enable');
await S('Runtime.enable');

async function setViewport(w, h) {
  await S('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 2, mobile: true });
}
async function nav(path) {
  await S('Page.navigate', { url: BASE + path });
  await sleep(1600);
}
async function evalJs(expression) {
  const r = await S('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  return r.result?.value;
}
async function shot(file) {
  const { data } = await S('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  writeFileSync(`${OUT}/${file}`, Buffer.from(data, 'base64'));
  console.log('saved', `${OUT}/${file}`);
}

const clickUnlock = `(() => { const b=[...document.querySelectorAll('.paywall .cta')].find(x=>/MTC/i.test(x.innerText)); if(b) b.click(); return !!b; })()`;
const clickChannel = (name) => `(() => { const c=[...document.querySelectorAll('.channel-card')].find(x=>new RegExp(${JSON.stringify(name)},'i').test(x.innerText)); if(c) c.click(); return !!c; })()`;
const clickCopy = `(() => { const b=[...document.querySelectorAll('.overlay .modal .cta.ghost')][0]; if(b) b.click(); return !!b; })()`;

async function run() {
  // ── mm 390 ──
  await setViewport(390, 844);
  await nav('/detail?lang=mm'); await evalJs(clickUnlock); await sleep(400); await shot('mm-unlock-modal-390.png');
  await nav('/report?lang=mm'); await sleep(300); await shot('mm-report-after-unlock-390.png');
  await nav('/community?lang=mm'); await evalJs(clickChannel('Telegram')); await sleep(400); await shot('mm-telegram-fallback-390.png');
  await evalJs(clickCopy); await sleep(250); await shot('mm-copy-link-390.png');

  // ── vi 390 ──
  await nav('/detail?lang=vi'); await evalJs(clickUnlock); await sleep(400); await shot('vi-unlock-modal-390.png');
  await nav('/report?lang=vi'); await sleep(300); await shot('vi-report-after-unlock-390.png');
  await nav('/community?lang=vi'); await evalJs(clickChannel('Zalo')); await sleep(400); await shot('vi-zalo-fallback-or-coming-soon-390.png');

  // ── zh regression ──
  await nav('/?lang=zh'); await sleep(300); await shot('zh-regression-390.png');

  // ── 430 viewport (unlock modal both langs) ──
  await setViewport(430, 932);
  await nav('/detail?lang=mm'); await evalJs(clickUnlock); await sleep(400); await shot('mm-unlock-modal-430.png');
  await nav('/detail?lang=vi'); await evalJs(clickUnlock); await sleep(400); await shot('vi-unlock-modal-430.png');
}

try {
  await run();
} finally {
  ws.close();
  chrome.kill();
}
console.log('done');
