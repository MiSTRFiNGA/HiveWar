# 📦 HiVE SWARM — store submission pack (copy-paste ready)

## Files
- CrazyGames upload: CG portal rejects our zips — upload the extracted `dist/crazygames/index.html`
  (single file, CG SDK adapter injected). Companion `dist/crazygames/psdk_adapter.js` is inlined at build.
- Poki upload: `dist/poki/hiveswarm-poki.zip` (Poki SDK adapter integrated)
- Covers (CrazyGames requires all three): `store/cover_16x9.png` (1920×1080) ·
  `store/cover_2x3_800x1200.png` (portrait) · `store/cover_1x1_800x800.png` (square) — TODO art pass
- Preview videos: `store/preview_landscape_1080p.mp4` + `store/preview_portrait_1080p.mp4`
  (15s real `?test=1` gameplay, H.264, no audio) — TODO capture pass

## Name
HiVE SWARM

## Tagline (short)
Grow the swarm. Mow the hive. Kill the Queen.

## Description
The hive came for the city. Bring an army.

Drag to steer your strike squad down a neon elevated highway while a WALL of alien biomorphs
floods toward you from the horizon. Shoot the gates before you hit them — every gate you feed
bullets gets better: bigger squad bonuses, fatter multipliers, heavier plasma weapons.

Grow from a lone blaster to a firing line of hundreds backed by hover-tanks. Rack up kill
streaks in the hundreds as acid splatters the road. Then the horizon darkens: a Hive Guardian
is coming — and behind ten of them, the Alien Queen is laying eggs in her chamber. Stop her
mid-lay to save the city, then take on the infinite Endless Hive.

- One-finger controls: drag left/right — your squad fires automatically
- Shootable gates: pump bullets into +squad / xmultiplier / weapon gates to upgrade them before you pass
- Mutation perks mid-run: Chain Lightning, Orbital Laser, Drone Escort and more
- 10 levels, each ending in a screen-filling boss with telegraphed attacks
- The Alien Queen finale: destroy her eggs, survive the acid lanes, end the hive
- Endless Hive mode + best-score chase after you beat the campaign
- Permanent upgrades between runs: damage, starting squad, weapons, tank drops

## Category / tags
Action · Arcade · Shooting · .io-style · Casual
Tags: swarm, horde, auto-shooter, aliens, cyberpunk, count-gates, run-and-gun, boss-fight,
upgrades, hypercasual, endless, sci-fi

## Controls text
Drag (mouse / touch) left and right to steer. Your squad fires automatically —
aim the stream at gates to power them up before you pass through.

## Technical answers (both platforms ask these)
- Engine: custom HTML5 Canvas (vanilla JS), single file, no backend
- Loads offline after first load: yes · Save data: localStorage only
- Orientation: portrait-first, responsive letterbox on desktop · Mobile-friendly: yes
- SDK: CrazyGames adapter (init + gameplayStart/Stop + rewarded revive/boosts + midgame at level end)
  in the CG build; Poki adapter (same hooks) in the Poki build — both via injected psdk_adapter
- Violence: stylized alien creatures only, neon-green "acid" effects, no human casualties
  (soldiers teleport out), no blood-red gore, no text chat
- Age rating: suitable for teens (stylized sci-fi action)
- Build size: ~40KB raw / ~14KB gzipped

## Review-pass checklist (do before hitting Submit)
- [ ] Test extracted index.html in CrazyGames' QA tool (dev portal → your game → QA) —
      verify midgame ad fires at level-clear and rewarded revive works on death screen
- [ ] Poki Inspector — same checks
- [ ] Generate + upload the three covers and two preview videos
- [ ] Paste description/controls/tags from this file
- [ ] Submit for review

## After acceptance
- Post game link + 1–3 UGC clips/day (same runbook as Skull Drift / Bone Crush)
- Trial-metric watch: median session length + retention → tune the global difficulty knob
  (see balance/ BALANCE_R4 sign-off; knob work parked for post-trial analytics)

## Cover art briefs (ComfyUI pass)
All three: neon cyberpunk highway receding to a vanishing point, dense wall of eyeless chitinous
aliens flooding forward under magenta/cyan city glow, small squad of glowing blue soldiers with
cyan rings firing bright tracer streams, green acid splatter, huge alien queen silhouette looming
at the horizon. Logo text "HiVE SWARM" in chromed neon. High contrast, mobile-thumbnail readable.
- 16:9 1920×1080 (hero shot, logo right third)
- 2:3 800×1200 (vertical, logo top)
- 1:1 800×800 (queen face close-up + logo)
