"""One-shot patcher: adds the FORGE hover-help map (owner request 2026-08-03).

Kept in qa/ rather than run inline so the tooltip text (which contains quotes and
apostrophes) is not mangled by shell heredoc quoting.
"""
import io

p = 'index.html'
s = io.open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


HELP = r'''
// ---- FORGE field help (owner request 2026-08-03: "if i hover over the title, it tells me what it does") ----
// Keyed by EDIT path with array indices normalised to '*', so one entry covers all 6 enemies /
// 10 levels / 6 weapons. Rendered as a native title= tooltip on every input AND on the column
// headers of the entity and weapon tables.
const FORGE_HELP = {
  'player.rofMul':  'Global fire-rate multiplier. Stacks on top of the weapon ROF and any Overclock perk. 1 = unchanged.',
  'player.dmgMul':  'Global damage multiplier applied to every bullet, on top of weapon damage and tier bonuses. 1 = unchanged.',
  'player.armor':   'Percent of squad losses cancelled (0-90). At 50, a bite that would cost 8 soldiers costs 4.',
  'player.bottomOffset': 'How far UP from the bottom edge the squad stands, in pixels. 192 = 80% down the screen. Raise it on a phone so your thumb is not covering the squad. The melee line moves with it, so bite distance never changes.',
  'ui.hpBars':      'Health bars over enemies. 0 = elites only, and only once damaged (this is why fodder Xenoids never showed one). 1 = every enemy once damaged. 2 = every enemy, always.',
  'world.horizonStart': 'Where the vanishing point sits at the START of a level, as a fraction of screen height. LOWER = horizon higher up = longer path and more travel time. Clamped 0.15-0.60.',
  'world.horizonEnd':   'Where the vanishing point has moved to by the time the BOSS arrives. The corridor ramps from START to here as the wave timer runs, so the walls close in as you advance.',
  'world.spawnBackPx':  'Extra distance above the screen that enemies spawn from. They sit at the vanishing point until they cross the horizon, so this is pure lead-in delay - the cheapest fix if enemies appear too fast, with no change to how the path looks.',
  'world.approachMul':  'Multiplies every enemy advance speed at once. 0.8 = a 20% slower swarm without editing each enemy SPEED row.',
  'kinds.*.hpBase': 'Health at level 1. Total health = HP BASE + HP/LVL x current level, so this sets how tough it is early.',
  'kinds.*.hpLvl':  'Extra health added PER CAMPAIGN LEVEL. This is the scaling knob: 2/lvl stays fodder all game, 10/lvl becomes a wall by level 10.',
  'kinds.*.spd':    'Movement speed down the corridor in px/sec, before the WORLD approach multiplier and the per-level bonus.',
  'kinds.*.r':      'Collision and draw radius in pixels. Bigger = easier to hit AND reaches the squad sooner.',
  'kinds.*.credits':'CREDITS PAID FOR A KILL - the run currency you spend in the shop between levels on soldier and weapon tiers and on perks. Tougher enemies pay more.',
  'kinds.*.weight': 'SPAWN WEIGHT: relative share of the spawn table, shown live as SPAWN %. Doubling it makes that enemy appear twice as often. Nothing to do with knockback.',
  'kinds.*.mass':   'KNOCKBACK WEIGHT: how heavy it feels when shot. Pushback = the weapon RECOIL divided by this, so 0.5 flies back twice as far as 1 and 3 barely budges. An enemy that DIES to the shot cannot be seen recoiling.',
  'kinds.*.minLvl': 'First campaign level this enemy can spawn on. Use it to hold a nasty type back until the player has a squad.',
  'kinds.*.sfxAttack':'Sample played when this enemy bites the squad.',
  'kinds.*.sfxDie': 'Sample played when this enemy dies.',
  'entities.*.scale':'Sprite size multiplier. 1 = the art at its authored size. Does not change the collision radius.',
  'entities.*.range':'Tank only: how far out from the squad centre each escort tank sits, in pixels.',
  'entities.*.yOff': 'Tank only: vertical trim. Positive moves both tanks UP the corridor from their default row.',
  'weapons.*.rof':  'Rounds per second. The whole volley (every lane and pellet) fires on each tick.',
  'weapons.*.dmg':  'Damage per pellet before squad size, tiers and multipliers. Volley damage is shared across every bolt, so more pellets does not mean more DPS.',
  'weapons.*.spread':'Total fan angle in RADIANS across this weapon pellets. 0 = one straight line, 0.62 = a wide cone. Needs a pellet count above 1 to be visible.',
  'weapons.*.recoil':'Knockback punch in pixels at enemy weight 1. Actual pushback = this divided by the enemy WEIGHT. 0 = no bounce.',
  'weapons.*.sfx':  'Firing sample for this weapon.',
  'spawnRate.*':    'Enemies spawned per second on this level, before the within-level ramp. This is the main difficulty dial.',
  'bossHp.*':       'Health of that level guardian. The last slot is the Queen, whose phases are set separately.',
  'gateInterval.*': 'Seconds between barrier pairs on this level. Lower = more barriers.',
  'rollers.interval':'Seconds between rolling hazards.',
  'rollers.pctArmored':'Percent of rollers that are armored. Armored ones cannot be shot and must be dodged.',
  'rollers.hp':     'Health of a breakable roller at level 1.',
  'rollers.hpLvl':  'Extra roller health per campaign level.',
  'rollers.speed':  'How fast rollers tumble down the corridor, px/sec.',
  'rollers.size':   'Roller draw and collision size in pixels.',
  'rollers.dmg':    'Soldiers lost when a roller reaches the squad.',
  'rollers.minLvl': 'First level rolling hazards appear on.',
  'balance.startCredits':'Credits the player begins a run with.',
  'balance.killCreditMul':'Multiplies every kill payout. 2 = twice the shop money.',
  'balance.shopCostMul':'Multiplies every shop price. 0.5 = half-price upgrades.',
  'bossY':          'How far DOWN the corridor a boss walks before stopping. Bigger = it comes closer to the squad.',
  'earlySquadVal':  'Size of the free soldier gift handed out about 12 seconds into level 1.',
};
function helpFor(path){
  const key = String(path || '').replace(/\.\d+/g, '.*');
  return FORGE_HELP[key] || '';
}
function hlp(path){ const t = helpFor(path); return t ? ' title="' + forgeEsc(t) + '"' : ''; }
'''

rep("function num(p,step,w,aria){", HELP.strip() + "\nfunction num(p,step,w,aria){")

rep(
  '''  return `<input type="number" step="${step||1}" ${w?`style="width:${w}px"`:''} ${aria?`aria-label="${forgeEsc(aria)}"`:''} data-p="${p}" value="${v}">`;''',
  '''  return `<input type="number" step="${step||1}" ${w?`style="width:${w}px"`:''} ${aria?`aria-label="${forgeEsc(aria)}"`:''}${hlp(p)} data-p="${p}" value="${v}">`;''')

rep(
  '''function snd(p,aria){ const cur=getP(p); return `<select data-p="${p}" data-str="1" ${aria?`aria-label="${forgeEsc(aria)}"`:''}>` +''',
  '''function snd(p,aria){ const cur=getP(p); return `<select data-p="${p}" data-str="1" ${aria?`aria-label="${forgeEsc(aria)}"`:''}${hlp(p)}>` +''')

rep(
  '''<th scope="col" style="width:64px">SCALE</th><th scope="col" style="width:64px">HP BASE</th><th scope="col" style="width:64px">HP/LVL</th><th scope="col" style="width:64px">SPEED</th><th scope="col" style="width:64px">RADIUS</th><th scope="col" style="width:64px">CREDITS</th><th scope="col" style="width:64px">SPAWN WT</th><th scope="col" style="width:64px">WEIGHT</th><th scope="col" style="width:64px">MIN LVL</th><th scope="col" style="width:64px">RANGE</th><th scope="col" style="width:64px">Y-OFF</th>''',
  '''<th scope="col" style="width:64px"${hlp('entities.0.scale')}>SCALE</th><th scope="col" style="width:64px"${hlp('kinds.0.hpBase')}>HP BASE</th><th scope="col" style="width:64px"${hlp('kinds.0.hpLvl')}>HP/LVL</th><th scope="col" style="width:64px"${hlp('kinds.0.spd')}>SPEED</th><th scope="col" style="width:64px"${hlp('kinds.0.r')}>RADIUS</th><th scope="col" style="width:64px"${hlp('kinds.0.credits')}>CREDITS</th><th scope="col" style="width:64px"${hlp('kinds.0.weight')}>SPAWN WT</th><th scope="col" style="width:64px"${hlp('kinds.0.mass')}>WEIGHT</th><th scope="col" style="width:64px"${hlp('kinds.0.minLvl')}>MIN LVL</th><th scope="col" style="width:64px"${hlp('entities.0.range')}>RANGE</th><th scope="col" style="width:64px"${hlp('entities.0.yOff')}>Y-OFF</th>''')

rep(
  '''<table><tr><th>WEAPON</th><th>ROF</th><th>DMG</th><th>SPREAD</th><th>RECOIL</th><th>FIRE SFX</th><th>TEST</th></tr>`;''',
  '''<table><tr><th>WEAPON</th><th${hlp('weapons.0.rof')}>ROF</th><th${hlp('weapons.0.dmg')}>DMG</th><th${hlp('weapons.0.spread')}>SPREAD</th><th${hlp('weapons.0.recoil')}>RECOIL</th><th${hlp('weapons.0.sfx')}>FIRE SFX</th><th>TEST</th></tr>`;''')

rep(
  '''      <div class="row">APPROACH SPEED × ${num('world.approachMul',0.05,64)}''',
  '''      <div class="row">ENEMY HEALTH BARS ${num('ui.hpBars',1,48)}
        <span class="hint">0 = elites only once damaged (this is why fodder Xenoids never showed one) &middot;
        1 = every enemy once damaged &middot; 2 = every enemy, always.</span></div>
      <div class="row">APPROACH SPEED × ${num('world.approachMul',0.05,64)}''')

io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
