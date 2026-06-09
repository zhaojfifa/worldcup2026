#!/usr/bin/env node
/**
 * Linked Historical Recap QA screenshots (zero-dep CDP). Requires dev server + the
 * QA_RECAP_TEMP finished mock matches (reverted after capture). Uses deep links
 * /detail?match_id=8 & /report?match_id=8 to render real finished matches.
 * Output: docs/qa_screenshots/real_data_zh_vi_verification_linked_recap/
 */
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';
const BASE = process.argv[2] || 'http://localhost:5173';
const OUT = 'docs/qa_screenshots/real_data_zh_vi_verification_linked_recap';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9377;
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
async function shot(file){const{data}=await S('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});writeFileSync(`${OUT}/${file}`,Buffer.from(data,'base64'));console.log('saved',file);}
for (const lang of ['zh','vi']) {
  await nav(`/?lang=${lang}`); await shot(`home-${lang}-390.png`);
  await nav(`/detail?lang=${lang}`); await shot(`detail-${lang}-current-390.png`);
  await nav(`/report?lang=${lang}`); await shot(`report-${lang}-current-390.png`);
  await nav(`/detail?match_id=8&lang=${lang}`); await shot(`detail-${lang}-finished-recap-390.png`);
  await nav(`/report?match_id=8&lang=${lang}`); await shot(`report-${lang}-finished-recap-390.png`);
}
await nav('/community?lang=vi'); await shot('community-vi-390.png');
ws.close(); chrome.kill();
console.log('done');
