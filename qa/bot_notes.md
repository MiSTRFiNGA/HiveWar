# HiVE SWARM test-bot contract

Run the game at `/?test=1`. After roughly 600 ms the bot must leave `title`, steer toward advantageous gates, and continue playing without synthetic input.

`window.__dbg()` is the stable automation surface. It currently returns:

- `state`, `level`, `squad`, `weapon`, `credits`, and `kills`
- live `enemies` and `bullets` counts
- boss state when present
- `testBot`, which must initially be `true`

The first real pointer/touch/keyboard input must hand control to the player. Automation should dispatch a trusted browser input event and then confirm `window.__dbg().testBot === false`. JavaScript-created events are intentionally insufficient because the game checks `event.isTrusted`.

Portal builds load `psdk_adapter.js` before the core script. Local/offline failures degrade to no-op SDK methods; ads return `false` instead of blocking play. CrazyGames receives an extracted `dist/crazygames/index.html` plus its adapter. Poki receives `dist/poki/hiveswarm-poki.zip`.

Do not make the bot depend on render timing or pixel colors. Poll `window.__dbg()` and use a bounded timeout.

## Round-1 verification

Verified headlessly through Chromium DevTools Protocol on 2026-07-15:

- `/?test=1` advanced from the title into `state: "play"`.
- The live dump reported active enemies and bullets with `testBot: true`.
- A browser-dispatched trusted mouse press changed `testBot` to `false` while play continued.
- The source `index.html` was observed only and was not edited by Codex.

## Round-2 verification

Verified in headless Chromium at level 6 with seeded spawning:

- Enemy pool contained all five kinds, including 11 winged divers and 7 telegraphing burrowers in the bounded sample.
- One Drone Escort stack created two drone shots through the shared bullet pool.
- One Orbital Laser stack entered an active 0.7-second sweep and exposed `laserActive: true` through `window.__dbg()`.
- Packaging tests remained 3/3 green after rebuilding both portal distributions.
