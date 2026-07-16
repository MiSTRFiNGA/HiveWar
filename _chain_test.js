require('./_headless_harness_stub.js');   // shared stubs
const H = globalThis.__H;
H.startRun('campaign');
// pack 300 cyber-mutants (kind 2) into a tight cluster
const K = H.EKIND[2];
for (let i = 0; i < 300; i++) {
  const e = H.enemies.alloc(); if (!e) break;
  e.kind = 2; e.x = 270 + (Math.random()*30-15); e.y = 400 + (Math.random()*30-15);
  e.vx = 0; e.vy = 0; e.baseX = e.x; e.phase = 0; e.mode = 0; e.t = 0;
  e.maxhp = e.hp = 3; e.r = K.r;
}
console.log('packed cyber-mutants:', H.enemies.count());
try {
  // kill one in the middle -> would previously chain-recurse to stack overflow
  H.enemies.each(e => { if (e.hp > 0 && Math.abs(e.x-270)<5) { H.damageEnemy(e, 999, e.x, e.y); return; } });
  console.log('CHAIN OK — survivors:', H.enemies.count());
} catch (err) {
  console.error('CHAIN FAILED:', err.message);
}
