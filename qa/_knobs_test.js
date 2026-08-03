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


let code = fs.readFileSync(__dirname + '/../_game_extract.js', 'utf8');
code += `
;globalThis.__H = { get G(){return G;}, startRun, update, draw, levelStart, CFG, EDIT,
  playerY, tankY, applyHorizon, knockBack, saveEdit, enemies, enemyRow, WEAPONS,
  get HORIZON_Y(){return HORIZON_Y;} };`;
(0, eval)(code);
const H = globalThis.__H;
let fails = 0;
const ok = (name, cond, extra) => { console.log((cond?'PASS  ':'FAIL  ')+name+(extra?'   '+extra:'')); if(!cond) fails++; };

// 1. player screen position
const pDefault = H.playerY();
H.EDIT.player.bottomOffset = 220;
ok('player screen position moves up', H.playerY() === H.CFG.H - 220, `default=${pDefault} tuned=${H.playerY()}`);
H.EDIT.player.bottomOffset = 25;

// 2. tank vertical offset
const tDefault = H.tankY();
const tank = H.EDIT.entities.find(e => e.id === 'vehicle.tank');
tank.yOff = 90;
ok('tank Y-offset moves up', H.tankY() === tDefault - 90, `default=${tDefault} tuned=${H.tankY()}`);
tank.yOff = 0;

// 3. corridor depth
const hDefault = H.HORIZON_Y;
H.EDIT.world.horizonPct = 0.25; H.applyHorizon();
const hDeep = H.HORIZON_Y;
ok('lower horizonPct = longer path', hDeep < hDefault, `0.407->${hDefault.toFixed(1)}  0.25->${hDeep.toFixed(1)} (path ${(H.CFG.H-hDefault).toFixed(0)}px -> ${(H.CFG.H-hDeep).toFixed(0)}px)`);
H.EDIT.world.horizonPct = 9; H.applyHorizon();
ok('horizonPct clamped', H.HORIZON_Y === H.CFG.H * 0.60, `clamped to ${H.HORIZON_Y.toFixed(1)}`);
H.EDIT.world.horizonPct = 0.407; H.applyHorizon();

// 4. spawn lead-in + approach speed
// force a dense wave so this is not a vacuous pass
const measureSpawn = (backPx, apprMul) => {
  H.startRun('campaign'); H.EDIT.spawnRate[0] = 40;
  H.EDIT.world.spawnBackPx = backPx; H.EDIT.world.approachMul = apprMul;
  for (let i=0;i<8;i++) H.update(0.1);
  let minY = 1e9, n = 0, sumV = 0;
  H.enemies.each(e => { n++; minY = Math.min(minY, e.y); sumV += e.vy; });
  return { n, minY, avgV: n ? sumV/n : 0 };
};
const base = measureSpawn(0, 1), back = measureSpawn(600, 1);
ok('spawn lead-in pushes the spawn point further back', back.n > 0 && back.minY < base.minY - 500,
   `default highest y=${base.minY.toFixed(0)} (n=${base.n})  +600px lead-in y=${back.minY.toFixed(0)} (n=${back.n})`);
const slow = measureSpawn(0, 0.5);
ok('approach speed multiplier slows the swarm', slow.avgV > 0 && slow.avgV < base.avgV * 0.6,
   `default avg vy=${base.avgV.toFixed(1)}  x0.5 avg vy=${slow.avgV.toFixed(1)}`);
H.EDIT.world.spawnBackPx = 0; H.EDIT.world.approachMul = 1;

// 5. knockback: same weapon, different enemy weight
H.startRun('campaign');
const mk = (kind, mass) => { H.EDIT.kinds[kind].mass = mass;
  const e = H.enemies.alloc(); e.kind = kind; e.mode = 0; e.y = 600; e.x = 270; e.hp = e.maxhp = 9999; e.kb = 0; e.t=0; e.vy=0; e.lane=0; return e; };
const light = mk(0, 0.5), heavy = mk(0, 0.5);   // same kind so speed is identical
H.EDIT.kinds[0].mass = 0.5; H.knockBack(light, 30);
H.EDIT.kinds[0].mass = 3;   H.knockBack(heavy, 30);
ok('lighter enemy takes more knockback', light.kb > heavy.kb, `mass0.5 kb=${light.kb.toFixed(1)}  mass3 kb=${heavy.kb.toFixed(1)}`);
const before = light.y;
for (let i=0;i<3;i++) H.update(0.05);
ok('knockback actually moves the enemy back up the corridor', light.y < before, `y ${before.toFixed(0)} -> ${light.y.toFixed(0)}`);

// 6. weapon recoil is per-weapon and FORGE-visible
ok('every weapon has a recoil value', H.WEAPONS.every(w => Number.isFinite(w.recoil)), H.WEAPONS.map(w=>w.name+':'+w.recoil).join('  '));

console.log(fails ? `\n${fails} CHECK(S) FAILED` : '\nALL CHECKS PASSED');
process.exit(fails ? 1 : 0);
