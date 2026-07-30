# 📦 HiVE WAR — store submission pack (copy-paste ready)

**Author:** Grok · **Updated:** 2026-07-30 (Order #3 Job 3)  
**Scope:** text / metadata / art-spec / portal-QA only. No art generation. Do not edit `index.html`.
**Note (Claude, 2026-07-30):** renamed from HiVE SWARM — that name now belongs to a different,
future title. Listing name/lockup below updated; `hiveswarm-poki.zip` build artifact name left
as-is (matches `build.py` + `qa/test_packaging.py`, not a player-facing string).

Balance note: `CG_KPI_TUNE_2026-07-29.json` is already merged (softer L1–2, minus-gates, EKIND[0].hp=1, startingSquad floor 10). No further balance work in this kit.

---

## Files

| Artifact | Path | Status |
|----------|------|--------|
| CrazyGames upload | Extracted `dist/crazygames/index.html` (CG portal **rejects zips from us**) | Build via `python build.py` |
| Poki upload | `dist/poki/hiveswarm-poki.zip` | Build via `python build.py` |
| Cover 16:9 | `store/cover_16x9.png` | **MISSING — art pass** |
| Cover 2:3 | `store/cover_2x3_800x1200.png` | **MISSING — art pass** |
| Cover 1:1 | `store/cover_1x1_800x800.png` | **MISSING — art pass** |
| Preview landscape | `store/preview_landscape_1080p.mp4` | **MISSING — capture pass** |
| Preview portrait | `store/preview_portrait_1080p.mp4` | **MISSING — capture pass** |

---

## Name / title treatment

**Listing name:** HiVE WAR  
**Lockup notes:** Keep the capital **i** in HiVE (brand). Avoid all-caps “HIVE WAR” in logo if it collides with generic hive games. Subtitle optional: “Grow the swarm.”

## Tagline (short)

Grow the swarm. Mow the hive. Kill the Queen.

## Short description (portal blurb, ~160–220 chars)

> Drag your neon strike squad down the elevated highway. Blast gates to grow the army, mow endless alien walls, and stop the Queen mid-lay. 10 boss levels + Endless Hive.

## Description (long — paste-ready)

```
The hive came for the city. Bring an army.

Drag to steer your strike squad down a neon elevated highway while a WALL of alien biomorphs
floods toward you from the horizon. Shoot the gates before you hit them — every gate you feed
bullets gets better: bigger squad bonuses, fatter multipliers, heavier plasma weapons.

Grow from a lone blaster to a firing line of hundreds backed by hover-tanks. Rack up kill
streaks in the hundreds as acid splatters the road. Then the horizon darkens: a Hive Guardian
is coming — and behind ten of them, the Alien Queen is laying eggs in her chamber. Stop her
mid-lay to save the city, then take on the infinite Endless Hive.

• One-finger controls: drag left/right — your squad fires automatically
• Shootable gates: pump bullets into +squad / xmultiplier / weapon gates before you pass
• Mutation perks mid-run: Chain Lightning, Orbital Laser, Drone Escort and more
• 10 levels, each ending in a screen-filling boss with telegraphed attacks
• The Alien Queen finale: destroy her eggs, survive the acid lanes, end the hive
• Endless Hive mode + best-score chase after you beat the campaign
• Permanent upgrades between runs: damage, starting squad, weapons, tank drops

No download. No account required to start. Desktop + mobile browser.
```

## Category / genre / tags

- **Primary genre:** Action / Arcade / Shooting  
- **Secondary:** .io-style horde · Casual run-and-gun  
- **Tags (paste):** swarm, horde, auto-shooter, aliens, cyberpunk, count-gates, run-and-gun, boss-fight, upgrades, hypercasual, endless, sci-fi, neon, squad

## Controls text (portal field)

Drag (mouse / touch) left and right to steer. Your squad fires automatically — aim the stream at gates to power them up before you pass through.

## Age rating answers (portal)

| Question (typical) | Answer |
|--------------------|--------|
| Violence | Stylized sci-fi combat vs alien biomorphs only; neon-green “acid”; no realistic gore |
| Human characters harmed? | No — human soldiers are player squad; enemies are aliens |
| Blood / gore | No red blood; green acid FX only |
| Text chat / UGC | None |
| Gambling / real-money | None |
| Suggested rating | Teen / 12+ (stylized action) — adjust if portal forces Everyone vs Teen |

## Technical answers (both platforms)

- Engine: custom HTML5 Canvas (vanilla JS), single file, no backend  
- Loads offline after first load: yes · Save data: localStorage only  
- Orientation: portrait-first, responsive letterbox on desktop · Mobile-friendly: yes  
- SDK: CrazyGames adapter (init + gameplayStart/Stop + rewarded revive/boosts + midgame at level end) in the CG build; Poki adapter (same hooks) in the Poki build — both via injected `psdk_adapter`  
- External links: none in playable builds  
- Build size (approx prior measurement): ~40KB raw / ~14KB gzipped game shell + assets under CG limits  

---

## Cover-art SPEC (exact sizes — do not generate here)

CrazyGames expects **three** stills (same family of art, different crops). Poki accepts similar hero/thumb assets.

| File | Pixels | Aspect | What it must depict |
|------|--------|--------|---------------------|
| `store/cover_16x9.png` | **1920×1080** | 16:9 landscape | Hero shot: neon elevated highway to vanishing point; dense wall of eyeless chitinous aliens flooding forward under magenta/cyan city glow; small squad of glowing blue soldiers with cyan rings firing bright tracers; green acid splatter; huge Alien Queen silhouette on the horizon. Logo **“HiVE WAR”** chromed neon in the **right third**. Mobile-thumbnail readable. |
| `store/cover_2x3_800x1200.png` | **800×1200** | 2:3 portrait | Same world, vertical crop. Logo **top third**. Squad lower-center firing upward/into depth; Queen or Guardian mass in upper half. No tiny UI chrome. |
| `store/cover_1x1_800x800.png` | **800×800** | 1:1 square | **Queen face / head close-up** + logo; high contrast silhouette; works at 100px favicon scale. |

**Optional extras (nice-to-have, not CG-blocking):**

| File | Pixels | Use |
|------|--------|-----|
| `store/cover_4x3.png` | 800×600 | Generic portal / social |
| `store/icon_512.png` | 512×512 | Icon / PWA |
| `store/thumb_720.png` | 1280×720 | Social share |

**Art rules:** no stolen IP, no real-world gore, no unreadable text under 24px at export, keep logo out of edges (safe margin ~5%).

## Preview video SPEC (capture pass — not done here)

| File | Resolution | Length | Codec | Content |
|------|------------|--------|-------|---------|
| `store/preview_landscape_1080p.mp4` | **1920×1080** | **15 s** | H.264, **no audio** | Real gameplay (`?test=1` or production build): 0–3s gate growth hook, 3–10s horde mow + boss tease, 10–15s Queen or big streak + title card |
| `store/preview_portrait_1080p.mp4` | **1080×1920** | **15 s** | H.264, **no audio** | Same beats, portrait capture or letterboxed vertical export |

---

## Portal-QA checklist (derived from CG / Poki practice)

### CrazyGames (dev portal → game → QA tool)

- [ ] Upload is **extracted playable** (`index.html` + relative assets) — **not** a zip (CG rejects our zips)
- [ ] Cold load: game becomes interactive with **≤ 1 meaningful click** after load
- [ ] `gameplayStart` fires when the run is actually playable (not stuck on a dead menu)
- [ ] `gameplayStop` on pause / level-end / death as wired
- [ ] Midgame ad path fires at **level clear** (Full Launch path; Basic may disable ads)
- [ ] Rewarded revive / boost path works from death UI when SDK present
- [ ] Desktop Chrome + Edge smoke; mobile touch drag steers correctly
- [ ] No absolute `file://` or cross-origin asset breaks; relative paths only
- [ ] Initial download well under **50 MB** (Basic) and **20 MB** if targeting mobile homepage
- [ ] File count ≤ **1500**
- [ ] No console-fatal errors on first run; game recovers from tab blur
- [ ] Covers (3) + previews (2) uploaded and preview correctly in portal
- [ ] Metadata pasted from this file (name, short, long, controls, tags, age)

### Poki (Inspector / preview)

- [ ] Upload `dist/poki/hiveswarm-poki.zip` accepted
- [ ] Poki SDK init + `gameLoadingFinished` + gameplayStart/Stop
- [ ] Commercial break hooks on death/restart as designed
- [ ] Same touch + desktop smoke as CG
- [ ] No external navigations / store links inside playable

### Pre-submit gate (from `CG_READINESS_AUDIT.md`)

- [ ] Queen finale + high-visibility assets finished by gameplay owner (Claude)
- [ ] Three covers + two videos exist on disk (Eric / art)
- [ ] Fresh `python build.py` after last gameplay change
- [ ] Owner of `index.html` signs browser smoke (first-load, touch, save/load, pause/resume, ads, offline)

---

## Review-pass checklist (do before hitting Submit)

- [ ] Test extracted index.html in CrazyGames QA tool  
- [ ] Poki Inspector — same checks  
- [ ] Generate + upload the three covers and two preview videos  
- [ ] Paste description / controls / tags / age answers from this file  
- [ ] Submit for review  

## After acceptance

- Post game link + 1–3 UGC clips/day (same runbook as Skull Drift / Bone Crush)  
- Trial-metric watch: median session length + retention → tune global difficulty knob post-trial  

## Handoff

| Who | Does |
|-----|------|
| **Grok** | This text/metadata kit + cover/video SPEC + portal-QA list (**done**) |
| **Claude** | Gameplay / Queen / `index.html` / SDK wiring verification |
| **Eric** | Art capture, portal create/submit, final QA click-through |
