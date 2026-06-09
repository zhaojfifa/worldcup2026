#!/usr/bin/env node
/**
 * Historical Recap separation QA screenshots (zero-dep CDP driver).
 * Temporary QA helper. Requires the dev server + the QA_RECAP_TEMP finished mock matches
 * (reverted after capture). Output: docs/qa_screenshots/historical_recap_separation/
 */
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const BASE = process.argv[2] || 'http://localhost:5173';
const OUT = 'docs/qa_screenshots/historical_recap_separation';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9355;
mkdirSync(OUT, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run','--no-default-browser-check',`--remote-debugging-port=${PORT}`,`--user-data-dir=/tmp/qa-chrome-${PORT}`,'about:blank'],{stdio:'ignore'});
async function getWsUrl(){for(let i=0;i<50;i++){try{const r=await fetch(`http://localhost:${PORT}/json/version`);const j=await r.json();if(j.webSocketDebuggerUrl)return j.webSocketDebuggerUrl;}catch{}await sleep(200);}throw new Error('no CDP');}
function cdp(ws){let id=0;const p=new Map();ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id);}});return{send:(method,params={},sessionId)=>new Promise((res,rej)=>{const mid=++id;p.set(mid,m=>m.error?rej(new Error(method+': '+JSON.stringify(m.error))):res(m.result));ws.send(JSON.stringify({id:mid,method,params,sessionId}));})};}
const ws=await(async()=>{const u=await getWsUrl();const s=new WebSocket(u);await new Promise((res,rej)=>{s.addEventListener('open',res);s.addEventListener('error',rej);});return s;})();
const {send}=cdp(ws);
const {targetId}=await send('Target.createTarget',{url:'about:blank'});
const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
const S=(m,p)=>send(m,p,sessionId);
await S('Page.enable');await S('Runtime.enable');
await S('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:2,mobile:true});
async function nav(path){await S('Page.navigate',{url:BASE+path});await sleep(1700);}
async function evalJs(expr){const r=await S('Runtime.evaluate',{expression:expr,awaitPromise:true,returnByValue:true});return r.result?.value;}
async function shot(file,full=true){const{data}=await S('Page.captureScreenshot',{format:'png',captureBeyondViewport:full});writeFileSync(`${OUT}/${file}`,Buffer.from(data,'base64'));console.log('saved',file);}

await nav('/?lang=vi'); await shot('home-vi-current-filtered-390.png'); await shot('home-vi-historical-recap-390.png');
await nav('/?lang=zh'); await shot('home-zh-regression-390.png');
await nav('/?lang=mm'); await shot('home-mm-regression-390.png');
// finished-match detail/report: open home, click a recap row (sets selected match), then capture
await nav('/?lang=vi'); await evalJs(`(()=>{const r=document.querySelector('.recap-row');if(r)r.click();return!!r;})()`); await sleep(900);
await shot('detail-vi-finished-recap-390.png');
await nav('/report?lang=vi'); await sleep(600); await shot('report-vi-finished-recap-390.png');
ws.close(); chrome.kill();
console.log('done');
