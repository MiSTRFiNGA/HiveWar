# iOS CI scaffolding — HiVE Swarm (INERT)

## Why this is blocked

| Requirement | Status |
|-------------|--------|
| Public GitHub repo → free macOS Actions minutes | Available |
| Capacitor iOS scaffold workflow | `.github/workflows/ios-scaffold.yml` |
| **Apple Developer Program ($99/yr)** | Eric must purchase — agents do not |
| Signing cert + provisioning profile | Requires the paid account |
| Device / TestFlight install | Needs signing |

Agents must **not** create Apple accounts or spend money.

## What Eric does after buying the program

1. Create an App ID / bundle id matching `com.empiregames.hiveswarm` (or a new reverse-DNS id you prefer).
2. Create a Distribution certificate + App Store provisioning profile.
3. Export the cert as `.p12` + download the `.mobileprovision`.
4. GitHub → Settings → Secrets → Actions:
   - `APPLE_CERTIFICATE_BASE64`
   - `APPLE_CERTIFICATE_PASSWORD`
   - `APPLE_PROVISIONING_PROFILE_BASE64`
   - `APPLE_TEAM_ID`
5. Run workflow **iOS scaffold (INERT)** with `attempt_archive=true` after wiring `xcodebuild` (follow-up once secrets exist).
6. Upload the IPA via Transporter / App Store Connect.

## Capacitor iOS notes

Example config: `capacitor.config.example.json`

- Copy `index.html` + `assets/` + `sounds/` into `www/` before `cap sync`
- PWA on GitHub Pages remains the **zero-cost iOS install path** (Add to Home Screen) until native is paid for

## Do not expect

- An IPA from CI today
- Side-loading without a developer cert
- Free App Store distribution
