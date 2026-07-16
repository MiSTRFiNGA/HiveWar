require('./_headless_harness_stub.js');
const H = globalThis.__H;
H.startRun('campaign');
H.G.perks = { 'Chain Lightning': 3, 'Orbital Laser': 3, 'Acid Rounds': 3 };
H.G.state = 'play';
H.offerPerks();
console.log('after offerPerks: state=', H.G.state, ' perkChoices=', JSON.stringify(H.perkChoices));
console.log(H.G.state === 'perk' && H.perkChoices.length === 0 ? 'REPRO: SOFT-LOCK (stuck on MUTATION READY, nothing to pick)' : 'no lock');
