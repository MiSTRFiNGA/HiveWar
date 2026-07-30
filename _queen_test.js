// Queen-finale verification harness.
// The store description advertises the L10 Alien Queen as the climax, and the CG readiness audit
// flagged her as an unverified content risk. This drives a godmode run straight to L10 and measures
// whether she is actually killable and how long it takes — a boss that cannot die inside a sane
// session is a shipping blocker even though the mechanics "exist".
require('./_headless_harness_stub.js');
const H = globalThis.__H;

H.startRun('campaign');
H.G.level = 10;
H.levelStart();

let step = 0, phaseSeen = {}, firstBossStep = null, killedStep = null;
let lastHp = null, hpAt = [];

for (step = 0; step < 90000; step++) {          // up to 9000s of sim
  if (H.G.squad < 40) H.G.squad = 40;           // godmode: keep a full firing line alive
  H.update(0.1);
  const st = H.state;
  if (st === 'perk') { H.pickPerkForce(); H.G.state = H.G.boss ? 'boss' : 'play'; }

  const B = H.G.boss;
  if (B) {
    if (firstBossStep === null) {
      firstBossStep = step;
      console.log(`boss spawned @${(step * 0.1).toFixed(0)}s queen=${!!B.queen} maxhp=${B.maxhp}`);
    }
    if (!phaseSeen[B.phase]) {
      phaseSeen[B.phase] = true;
      console.log(`  -> phase ${B.phase} @${(step * 0.1).toFixed(0)}s hp=${Math.round(B.hp)}`);
    }
    if (step % 2000 === 0) hpAt.push(`${(step * 0.1).toFixed(0)}s:${Math.round(B.hp)}`);
    if (B.dead && killedStep === null) {
      killedStep = step;
      console.log(`QUEEN KILLED @${(step * 0.1).toFixed(0)}s`);
    }
    lastHp = B.hp;
  }

  if (st === 'win') { console.log(`WIN @${(step * 0.1).toFixed(0)}s`); break; }
  if (st === 'dead') { H.G.state = 'play'; }    // ignore deaths; we are measuring TTK not survival
  H.draw();
}

console.log('--- result ---');
console.log('boss spawned at step:', firstBossStep);
console.log('phases reached:', Object.keys(phaseSeen).join(',') || 'NONE');
console.log('killed:', killedStep !== null ? `yes @${(killedStep * 0.1).toFixed(0)}s` : 'NO — survived the whole sim');
console.log('final boss hp:', lastHp === null ? 'n/a' : Math.round(lastHp));
console.log('hp samples:', hpAt.join(' '));
console.log('endless unlocked:', !!(H.G.meta && H.G.meta.endless));
