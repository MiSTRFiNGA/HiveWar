# HiVE SWARM — CrazyGames Readiness Audit

Date: 2026-07-30  
Scope: read-only audit. `index.html` was deliberately not opened or inspected.

## Verdict: NOT READY TO SUBMIT

The project has a credible portal-build pipeline and prior gameplay/harness evidence, but the documented submission package is incomplete and platform QA has not been completed.

## Verified strengths

- `build.py` produces an extracted CrazyGames artifact and a Poki zip, with the platform adapter injected before game code.
- `qa/test_packaging.py` covers adapter ordering, platform-token replacement, and the expected archive contents.
- The repository contains a CrazyGames output area, Poki zip, `psdk_adapter.js`, gameplay evidence images, a balance/R6 tuning record, and a detailed store-submission guide.
- The roadmap records a clean ten-level headless run (with a known early-difficulty caveat) and recorded browser verification for several production passes.

## Submission blockers

1. **Store art is missing.** `store/SUBMISSION.md` marks all three required covers as TODO: 16:9, portrait, and square.
2. **Preview video is missing.** Both required 15-second real-gameplay captures are marked TODO.
3. **Portal QA is incomplete.** CrazyGames QA still needs an extracted-build test confirming the midgame ad at level clear and rewarded revive on death; Poki Inspector needs the equivalent pass.
4. **Core-content risks remain.** The roadmap lists the Alien Queen egg/hatchling/tail-swing mechanics and several art integrations as unfinished. These are material because the store description advertises the Queen finale.
5. **Static review is intentionally incomplete.** Because `index.html` is Claude-owned and actively off-limits, this audit does not certify runtime script safety, SDK call timing, asset references, or the final rendered presentation.

## Recommended release gate

1. Finish and verify Queen finale mechanics plus the listed high-visibility asset gaps.
2. Create the three covers and two preview videos called out in `store/SUBMISSION.md`.
3. Build fresh CG/Poki artifacts, then run the respective portal QA tools against them.
4. Have the owner of `index.html` run final browser smoke coverage for first-load, touch controls, save/load, pause/resume SDK hooks, midgame ad, rewarded revive, and offline launch.
5. Re-audit the final extracted CG artifact after those results are attached.

## Test note

I attempted to invoke the packaging unit test from outside its drive; Python rejected the cross-drive test path before test discovery/import. I did not retry from the project directory because that test's build path reads the prohibited source `index.html`.
