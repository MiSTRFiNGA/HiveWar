// Headless reproduction harness for the level-2 freeze.
// Stubs Canvas2D/DOM/Audio, loads the real game script, drives it through levels,
// and reports the exact state + stack trace when anything throws.
'use strict';
const fs = require('fs');

function makeCtx() {
  const grad = { addColorStop() {} };
  return new Proxy({
    canvas: { width: 540, height: 960 },
    createLinearGradient: () => grad,
    createRadialGradient: () => grad,
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
const doc = {
  getElementById: id => makeCanvas(),
  createElement: () => makeCanvas(),
  addEventListener(t, f) { (listeners[t] = listeners[t] || []).push(f); },
  body: { appendChild() {} }, documentElement: { style: {} },
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
