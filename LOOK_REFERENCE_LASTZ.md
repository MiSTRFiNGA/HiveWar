# HiVE SWARM — Look Reference: "Last Z: Survival Shooter"

Source: https://www.youtube.com/shorts/UJBpCkelBBU (42 s), watched frame-by-frame by
Claude 2026-07-15 at Eric's direction. **This is how Eric wants HiVE SWARM to look.**

## The core visual formula

Vertical (9:16-friendly) **street corridor crowd-runner shooter**:

1. **Camera:** high-angle top-down, tilted so the road is a deep corridor running
   away from the player toward the horde at the top. Squad anchored at the bottom
   ~quarter, enemies flow downward toward it.
2. **One → army arc:** the run starts with a single unit walking backward down the
   street; by the end the bottom of the screen is a dense wedge/crescent
   **crowd formation of dozens of identical gunners**. Watching the swarm grow IS
   the power fantasy.
3. **Gate/pickup lane mechanics** on the road:
   - Recruits standing at the roadside with a **bright yellow outline glow** and a
     floating **+1 / +2 / +3** — walk near to absorb them into the swarm.
   - **Breakable number obstacles** (barrels, tire stacks) with big bold white
     countdown numbers (10, 60, 70, 80, 200, 240) that tick down under fire and
     pop a reward/blocker when reduced to zero.
   - **Red hazard panels** with negative numbers (-7, -10, -76, -100) and an angry
     enemy icon — penalties/damage to avoid; **blue panels** (+2, +8, ammo icon)
     are buffs. Blue = gain, red = loss, everywhere and instantly readable.
4. **The bullet wall:** the money shot. Escalating from one tracer line to
   **dozens of parallel vertical tracer columns** (golden/orange-white, later mixed
   red) filling the whole road width, with muzzle flashes rippling along the squad
   front. Massive overdraw, additive glow, screen-filling — deliberately excessive.
5. **Enemy horde:** a shambling mass pouring in from the top, individually weak,
   visually uniform, with small red health bars; mini-boss moments (a turret
   gunner, "-100" panel, ~"66" HP tag) break the rhythm.
6. **Feedback juice:** floating damage numbers, red hit flashes on the horde
   front, green XP/pickup orbs drifting from kills, thin green health bar over the
   leader, occasional yellow-outlined elite recruits mid-road.
7. **Victory beat:** the swarm stops and **celebrates — arms up, dancing** — while a
   kill-feed banner shows "[player] got [player]" (social/PvP flavor even in a PvE
   run). End on the crowd, not on a menu.

## Art contrast that makes it work

- **World:** realistic, gritty, muted — cracked asphalt, road markings, rusted
  sidings, junk piles, hard daylight shadows. Nothing cartoonish about the set.
- **Gameplay layer:** loud arcade UI floating ON that world — huge white impact
  numbers, saturated blue/red panels, yellow outline glows, golden tracers.
  The realism of the street makes the arcade layer pop.

## Mapping to HiVE SWARM (cyberpunk skin, DESIGN.md v1.0)

| Last Z element | HiVE SWARM translation |
|---|---|
| Zombie horde | corrupted drone/synth swarm pouring down a neon street canyon |
| Blue-clad gunner crowd | player's hive of cyber-runners; identical silhouette, cyan rim-light |
| Yellow-outline recruits | hackable street units with cyan `+N` hologram tags |
| Barrel/tire number blockers | firewall crates / server stacks with countdown glyphs |
| Red/blue panels | red ICE debuffs vs cyan daemon buffs |
| Golden bullet wall | neon tracer wall (cyan/magenta), additive bloom |
| Green orbs | data shards |
| Victory dance + kill feed | swarm emote + net-handle kill feed banner |

**Non-negotiables to keep:** corridor camera, one→army growth curve, instantly
readable +blue/−red number language, escalating full-width tracer wall, celebration
ending. Those five carry the entire feel of the reference.
