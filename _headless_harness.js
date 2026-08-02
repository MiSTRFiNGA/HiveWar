// Headless reproduction harness for the level-2 freeze.
// Stubs Canvas2D/DOM/Audio, loads the real game script, drives it through levels,
// and reports the exact state + stack trace when anything throws.
'use strict';
const fs = require('fs');

function makeCtx() {
  const grad = { addColorStop() {} };
  return new Proxy({
    canvas: { width: 540, height: 960 },
    createLinearGradient: (...a) => { if (a.some(v => !Number.isFinite(v))) throw new Error('createLinearGradient non-finite: ' + a); return grad; },
    createRadialGradient: (...a) => { if (a.some(v => !Number.isFinite(v))) throw new Error('createRadialGradient non-finite: ' + a); return grad; },
    createPattern: () => ({}),
    getImageData: () => ({ data: [] }),
    measureText: () => ({ width: 10 }),
    setLineDash() {}, save() {}, restore() {}, beginPath() {}, closePath() {},
    moveTo() {}, lineTo() {}, quadraticCurveTo() {}, bezierCurveTo() {}, arc() {},
    ellipse() {}, rect() {}, fill() {}, stroke() {}, clip() {}, fillRect() {},
    strokeRect() {}, clearRect() {}, fillText() {}, strokeText() {}, translate() {},
    scale() {}, rotate() {}, drawImage() {}, transform() {}, setTransform() {},
    resetTransform() {}, arcTo() {}, roundRect() {},
  }, { get(t, p) { return p in t ? t[p] : (typeof p === 'string' ? () => {} : undefined); },
       set(t, p, v) { t[p] = v; return true; } });
}
function makeCanvas() {
  return { width: 540, height: 960, style: {}, getContext: () => makeCtx(),
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 540, height: 960 }),
    addEventListener() {} };
}
const store = {};
global.localStorage = { getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
// Minimal IndexedDB stub so FORGE's mediaDB() path initialises under Node (F1b migration).
// Stores records in-memory; enough to exercise hydrateMedia / save paths without a browser.
(function stubIndexedDB() {
  const dbs = new Map();
  function reqResult(value, err) {
    const r = { result: value, error: err || null, onsuccess: null, onerror: null, onupgradeneeded: null };
    queueMicrotask(() => {
      if (err) { if (r.onerror) r.onerror({ target: r }); }
      else if (r.onsuccess) r.onsuccess({ target: r });
    });
    return r;
  }
  function storeAPI(bucket) {
    return {
      put(val, key) { if (key !== undefined) bucket.set(key, val); else if (val && val.id != null) bucket.set(val.id, val); else bucket.set(String(bucket.size), val); return reqResult(key); },
      get(key) { return reqResult(bucket.has(key) ? bucket.get(key) : undefined); },
      delete(key) { bucket.delete(key); return reqResult(undefined); },
      clear() { bucket.clear(); return reqResult(undefined); },
      getAll() { return reqResult([...bucket.values()]); },
      openCursor() {
        const entries = [...bucket.entries()];
        let i = 0;
        const cursorReq = { result: null, onsuccess: null, onerror: null };
        const step = () => {
          if (i >= entries.length) { cursorReq.result = null; if (cursorReq.onsuccess) cursorReq.onsuccess({ target: cursorReq }); return; }
          const [k, v] = entries[i++];
          cursorReq.result = { key: k, value: v, continue: () => queueMicrotask(step) };
          if (cursorReq.onsuccess) cursorReq.onsuccess({ target: cursorReq });
        };
        queueMicrotask(step);
        return cursorReq;
      },
    };
  }
  global.indexedDB = {
    open(name, version) {
      if (!dbs.has(name)) dbs.set(name, new Map());
      const bucket = dbs.get(name);
      const r = {
        result: null, error: null, onsuccess: null, onerror: null, onupgradeneeded: null,
      };
      queueMicrotask(() => {
        const db = {
          objectStoreNames: { contains: () => true },
          createObjectStore: () => storeAPI(bucket),
          transaction: () => ({
            objectStore: () => storeAPI(bucket),
            oncomplete: null, onerror: null,
          }),
          close() {},
        };
        r.result = db;
        if (r.onupgradeneeded) r.onupgradeneeded({ target: r });
        if (r.onsuccess) r.onsuccess({ target: r });
      });
      return r;
    },
    deleteDatabase(name) { dbs.delete(name); return reqResult(undefined); },
  };
  global.IDBKeyRange = { bound: () => ({}), only: () => ({}) };
})();
global.performance = { now: () => Date.now() };
global.requestAnimationFrame = () => 0;   // we drive the loop manually
global.cancelAnimationFrame = () => {};
class Img { constructor() { this.ok = false; setTimeout(() => { this.onload && this.onload(); }, 0); }
  set src(v) { this._src = v; } get src() { return this._src; } }
global.Image = Img;
global.AudioContext = function () { return { createGain: () => ({ connect() {}, gain: { value: 1, setValueAtTime() {} } }),
  createOscillator: () => ({ connect() {}, start() {}, stop() {}, frequency: { setValueAtTime() {}, value: 0 } }),
  createBuffer: () => ({ getChannelData: () => new Float32Array(1) }),
  createBufferSource: () => ({ connect() {}, start() {}, buffer: null }),
  destination: {}, currentTime: 0, sampleRate: 44100, resume() {}, state: 'running' }; };
global.webkitAudioContext = global.AudioContext;
const listeners = {};
function makeEl(tag) {
  // Lightweight DOM element stub — enough for FORGE UI init (appendChild / style / dataset).
  if (tag === 'canvas') return makeCanvas();
  const kids = [];
  const byIdLocal = new Map();
  const el = {
    tagName: String(tag || 'div').toUpperCase(),
    style: {}, dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
    children: kids, childNodes: kids,
    appendChild(c) { kids.push(c); if (c && c.id) byIdLocal.set(c.id, c); return c; },
    removeChild(c) { const i = kids.indexOf(c); if (i >= 0) kids.splice(i, 1); return c; },
    insertBefore(c) { kids.push(c); return c; },
    setAttribute(k, v) { if (k === 'id') { el.id = v; byIdLocal.set(v, el); } },
    getAttribute: () => null, removeAttribute() {},
    addEventListener() {}, removeEventListener() {},
    querySelector(sel) {
      if (!sel) return null;
      if (sel.startsWith('#')) {
        const id = sel.slice(1);
        if (byIdLocal.has(id)) return byIdLocal.get(id);
        // FORGE builds markup via innerHTML — materialise missing ids on demand.
        const child = makeEl('div'); child.id = id; byIdLocal.set(id, child); kids.push(child); return child;
      }
      if (sel.startsWith('.')) {
        const child = makeEl('div'); child.className = sel.slice(1); kids.push(child); return child;
      }
      return makeEl('div');
    },
    querySelectorAll: () => [],
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 100, height: 40 }),
    focus() {}, blur() {}, click() {},
    innerHTML: '', textContent: '', value: '', type: '', id: '', className: '',
  };
  return el;
}
const elCache = new Map();
function byId(id) {
  if (id === 'game' || id === 'hud') return makeCanvas();
  if (!elCache.has(id)) elCache.set(id, makeEl('div'));
  return elCache.get(id);
}
const doc = {
  getElementById: byId,
  createElement: tag => makeEl(tag),
  createTextNode: t => ({ textContent: t }),
  querySelector: sel => {
    if (!sel) return null;
    if (sel.startsWith('#')) return byId(sel.slice(1));
    return makeEl('div');
  },
  querySelectorAll: () => [],
  addEventListener(t, f) { (listeners[t] = listeners[t] || []).push(f); },
  body: makeEl('body'), documentElement: { style: {} },
  head: makeEl('head'),
};
global.document = doc;
global.location = { search: '' };
global.window = global;
global.addEventListener = (t, f) => doc.addEventListener(t, f);
global.PSDK = null;
global.devicePixelRatio = 1;
global.innerWidth = 540; global.innerHeight = 960;

let code = fs.readFileSync(__dirname + '/_game_extract.js', 'utf8');
// strip 'use strict' const-redeclare safety: run in function scope, expose globals we poke
code += `
;globalThis.__H = { get G(){return G;}, startRun, update, draw, levelStart, BAL, CFG,
  get state(){return G.state;}, get perkChoices(){return typeof perkChoices!=='undefined'?perkChoices:[];},
  pickPerkForce(){ if(typeof perkChoices!=='undefined'&&perkChoices[0]){G.perks[perkChoices[0]]=(G.perks[perkChoices[0]]||0)+1;} },
};`;
try { (0, eval)(code); } catch (e) { console.error('LOAD ERROR:', e.stack); process.exit(1); }

const H = globalThis.__H;
H.startRun('campaign');
console.log('started. level=', H.G.level, 'squad=', H.G.squad);
let step = 0, lastLevel = H.G.level, lastState = H.state;
try {
  for (step = 0; step < 40000; step++) {   // ~4000s of sim
    H.update(0.1);
    const st = H.state;
    if (st === 'perk') { H.pickPerkForce(); H.G.state = H.G.boss ? 'boss' : 'play'; }
    else if (st === 'shop') { H.levelStart(); }   // auto-deploy next level
    else if (st === 'win' || st === 'dead') { console.log('reached', st, 'at level', H.G.level); break; }
    H.draw();
    if (H.G.level !== lastLevel) { console.log(`--> entered level ${H.G.level} at step ${step} (t=${(step*0.1).toFixed(0)}s) squad=${H.G.squad}`); lastLevel = H.G.level; }
  }
  console.log('SIM ENDED clean. final level', H.G.level, 'state', H.state, 'steps', step);
} catch (e) {
  console.error(`\n*** THREW at step ${step} (t=${(step*0.1).toFixed(1)}s) level=${H.G.level} state=${H.state} squad=${H.G.squad} ***`);
  console.error(e.stack);
}
