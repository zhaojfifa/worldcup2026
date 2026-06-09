#!/usr/bin/env node
/**
 * Scout Intelligence Rewrite QA screenshots (zero-dep CDP driver).
 * Temporary QA helper — NOT part of the production build. Requires a running dev server.
 *
 * Full-page captures of the rewritten Detail/Report (evidence strip, scout verdict,
 * factor source/impact/interpretation, contrarian, watch) for vi & mm, plus community,
 * zh regression, and the unlock modal interaction.
 *
 * Usage: node scripts/qa/intel_rewrite_shots.mjs [BASE_URL]
 * Output: docs/qa_screenshots/intelligence_rewrite/
 */
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const BASE = process.argv[2] || 'http://localhost:5173';
const OUT = 'docs/qa_screenshots/intelligence_rewrite';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9344;
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

async function setViewport(w, h) { await S('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 2, mobile: true }); }
async function nav(path) { await S('Page.navigate', { url: BASE + path }); await sleep(1700); }
async function evalJs(expression) { const r = await S('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }); return r.result?.value; }
async function shot(file, fullPage = true) {
  const { data } = await S('Page.captureScreenshot', { format: 'png', captureBeyondViewport: fullPage });
  writeFileSync(`${OUT}/${file}`, Buffer.from(data, 'base64'));
  console.log('saved', `${OUT}/${file}`);
}
const clickUnlock = `(() => { const b=[...document.querySelectorAll('.paywall .cta')].find(x=>/MTC/i.test(x.innerText)); if(b) b.click(); return !!b; })()`;

async function run() {
  for (const [w, h] of [[390, 844], [430, 932]]) {
    await setViewport(w, h);
    for (const lang of ['vi', 'mm']) {
      await nav(`/report?lang=${lang}`); await shot(`report-${lang}-${w}.png`);
      await nav(`/detail?lang=${lang}`); await shot(`detail-${lang}-${w}.png`);
    }
  }
  // community + zh regression + unlock modal at 390
  await setViewport(390, 844);
  await nav('/community?lang=vi'); await shot('community-vi-390.png');
  await nav('/community?lang=mm'); await shot('community-mm-390.png');
  await nav('/report?lang=zh'); await shot('report-zh-regression-390.png');
  await nav('/detail?lang=vi'); await evalJs(clickUnlock); await sleep(400); await shot('detail-vi-unlock-modal-390.png', false);
  await nav('/detail?lang=mm'); await evalJs(clickUnlock); await sleep(400); await shot('detail-mm-unlock-modal-390.png', false);
}
try { await run(); } finally { ws.close(); chrome.kill(); }
console.log('done');
