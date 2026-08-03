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
  playerY, tankY, muzzleY, applyHorizon, knockBack, saveEdit, enemies, bullets, fire, enemyRow, WEAPONS,
  applyEditWeapons, BG_ZOOM_START, BG_ZOOM_MAX,
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

// 3. corridor depth RAMPS across the level
H.startRun('campaign'); H.G.state='play'; H.G.levelT = 0; H.applyHorizon();
const hOpen = H.HORIZON_Y;
H.G.state='boss'; H.applyHorizon();
const hBoss = H.HORIZON_Y;
ok('path depth ramps deep->close across the level', hOpen < hBoss,
   `start ${hOpen.toFixed(0)} (path ${(H.CFG.H-hOpen).toFixed(0)}px)  ->  boss ${hBoss.toFixed(0)} (path ${(H.CFG.H-hBoss).toFixed(0)}px)`);
ok('start depth honours world.horizonStart 0.15', Math.abs(hOpen - H.CFG.H*0.15) < 1, `${hOpen.toFixed(1)} vs ${(H.CFG.H*0.15).toFixed(1)}`);
ok('boss depth honours world.horizonEnd 0.43', Math.abs(hBoss - H.CFG.H*0.43) < 1, `${hBoss.toFixed(1)} vs ${(H.CFG.H*0.43).toFixed(1)}`);
H.EDIT.world.horizonStart = 9; H.EDIT.world.horizonEnd = 9; H.applyHorizon();
ok('horizon clamped', H.HORIZON_Y === H.CFG.H * 0.60, `clamped to ${H.HORIZON_Y.toFixed(1)}`);
H.EDIT.world.horizonStart = 0.15; H.EDIT.world.horizonEnd = 0.43; H.G.state='play'; H.applyHorizon();

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


// 7. bolts originate at the soldier's top-centre and FOLLOW the squad's screen position
const fireOrigins = (bottomOffset, squad) => {
  H.startRun('campaign'); H.G.state='play'; H.EDIT.player.bottomOffset = bottomOffset; H.G.squad = squad; H.G.weapon = 1;
  H.bullets.each(b => H.bullets.release(b));
  H.fire(999);   // force one volley
  const out = []; H.bullets.each(b => out.push({x:b.x, y:b.y, vx:b.vx}));
  return out;
};
const lowSquad = fireOrigins(192, 1);
ok('bolts spawn at the sprite muzzle, not a hardcoded row',
   lowSquad.length > 0 && Math.abs(lowSquad[0].y - H.muzzleY()) < 12,
   `bolt y=${lowSquad[0] && lowSquad[0].y.toFixed(0)}  muzzleY=${H.muzzleY().toFixed(0)}  playerY=${H.playerY().toFixed(0)}`);
const moved = fireOrigins(400, 1);
ok('muzzle follows the squad when SCREEN POSITION moves',
   Math.abs(moved[0].y - lowSquad[0].y) > 190, `y ${lowSquad[0].y.toFixed(0)} -> ${moved[0].y.toFixed(0)} after +208px move`);
H.EDIT.player.bottomOffset = 192;

// 8. spread actually fans at 1 lane (the regression Eric reported)
H.EDIT.weapons[1].spread = 0.45; H.WEAPONS[1].spread = 0.45;
const oneLane = fireOrigins(192, 1);
const vxs = oneLane.map(b => b.vx);
ok('Spread Gun fans with a single lane (squad 1)', oneLane.length === H.WEAPONS[1].n && Math.max(...vxs) - Math.min(...vxs) > 50,
   `${oneLane.length} bolts, vx spread ${(Math.max(...vxs)-Math.min(...vxs)).toFixed(0)}`);

// 9. lane ladder keyed to SQUAD, not level
const laneCount = squad => { const o = fireOrigins(192, squad); return new Set(o.map(b => Math.round(b.x))).size; };
const l1 = laneCount(1), l10 = laneCount(10), l20 = laneCount(20);
ok('lane ladder is 1 / 2 / 3 by squad size', l1 === 1 && l10 === 2 && l20 === 3, `squad 1->${l1} lanes, 10->${l10}, 20->${l20}`);
const three = fireOrigins(192, 20);
const centreX = Math.round(H.G.px), centre = three.filter(b => Math.round(b.x) === centreX), flank = three.filter(b => Math.round(b.x) !== centreX);
ok('centre lane sits ahead of the flankers', centre.length && flank.length && centre[0].y < flank[0].y,
   `centre y=${centre[0] && centre[0].y.toFixed(0)}  flank y=${flank[0] && flank[0].y.toFixed(0)}`);


// 10. weapon roster: canonical names + the new Flamethrower
const names = H.WEAPONS.map(w => w.name);
ok('weapon names match DESIGN.md ladder', names[1] === 'Twin Plasma' && names[2] === 'Scatter Rail', names.join(' / '));
const ft = H.WEAPONS[5];
ok('Flamethrower exists as weapon 6', !!ft && ft.name === 'Flamethrower' && ft.burn > 0 && ft.life > 0,
   ft ? `rof=${ft.rof} dmg=${ft.dmg} n=${ft.n} spread=${ft.spread} life=${ft.life}s burn=${ft.burn}` : 'MISSING');

// flame puffs must expire (range limit) instead of flying off-screen
H.startRun('campaign'); H.G.state='play'; H.G.weapon = 5; H.G.squad = 1;
H.bullets.each(b => H.bullets.release(b));
H.fire(999);
const born = H.bullets.count();
const spawnY = []; H.bullets.each(b => spawnY.push(b.y));
for (let i=0;i<12;i++) H.update(0.05);   // 0.6s > the 0.42s puff life (auto-fire keeps making new ones)
let farthest = 0; H.bullets.each(b => { farthest = Math.max(farthest, H.muzzleY() - b.y); });
ok('flame puffs expire at max reach instead of crossing the screen',
   born > 0 && farthest < 200, `${born} puffs per volley, farthest live puff ${farthest.toFixed(0)}px from the muzzle (a normal bolt would be off-screen)`);
const reach = Math.max(...spawnY) - Math.min(...spawnY.concat([H.muzzleY() - 260]));
ok('flame is short-range vs a bolt', ft.spd < 1, `speed factor ${ft.spd} of a normal bolt, ${(640*ft.spd*ft.life).toFixed(0)}px reach`);

// burn keeps ticking after the stream stops
H.startRun('campaign');
const victim = H.enemies.alloc();
Object.assign(victim, {kind:1, mode:0, y:500, x:H.G.px, hp:5000, maxhp:5000, r:24, vy:0, t:0, lane:0, kb:0, phase:1, crowd:0, burnT:0});
victim.burnT = 1.6; victim.burnDps = 2.4;
const hpBefore = victim.hp;
for (let i=0;i<10;i++) H.update(0.05);
ok('flamethrower burn ticks damage over time', victim.hp < hpBefore, `hp ${hpBefore} -> ${victim.hp.toFixed(1)} with no further hits`);

// 11. readability + background
ok('background zoom is 100% -> 150%', H.BG_ZOOM_START === 1.0 && H.BG_ZOOM_MAX === 1.5, `${H.BG_ZOOM_START*100}% -> ${H.BG_ZOOM_MAX*100}%`);
ok('hp bar mode knob exists', H.EDIT.ui && Number.isFinite(H.EDIT.ui.hpBars), `ui.hpBars=${H.EDIT.ui && H.EDIT.ui.hpBars}`);

// 12. FORGE hover help resolves for indexed paths
// helpFor lives inside the FORGE closure, so assert against the source text instead
const src = fs.readFileSync(__dirname + '/../index.html', 'utf8');
const helpKeys = (src.match(/'(?:kinds|weapons|entities|world|player|ui|rollers|balance)\.[^']*':\s*'/g) || []).length;
ok('FORGE hover-help map is wired', /const FORGE_HELP = \{/.test(src) && /function hlp\(path\)/.test(src) && helpKeys >= 25,
   `${helpKeys} help entries, hlp() applied to num()/snd()/table headers`);
ok('credits + hp-per-level are explained', /CREDITS PAID FOR A KILL/.test(src) && /Extra health added PER CAMPAIGN LEVEL/.test(src));

console.log(fails ? `\n${fails} CHECK(S) FAILED` : '\nALL CHECKS PASSED');
process.exit(fails ? 1 : 0);
