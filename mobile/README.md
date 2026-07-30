# Mobile packaging notes — HiVE Swarm

## Android (working today)

Local **signed** APK (HiVEMiND only):

```powershell
pwsh -File D:\Dev\_mobile\build_apk.ps1 -Game HiveSwarm -Version 1.0
```

- Capacitor project lives under `D:\Dev\_mobile\hiveswarm\` (not committed to this public repo).
- Observed Capacitor Android settings (local project, 2026-07-30):
  - `minSdkVersion = 24`
  - `compileSdkVersion = 36`
  - `targetSdkVersion = 36`
  - `applicationId = com.empiregames.hiveswarm`
  - Permission: `INTERNET` only

### GitHub Actions — unsigned APK

Workflow: `.github/workflows/apk-unsigned.yml`

- Triggers: push tag `v*` or manual `workflow_dispatch`
- Builds **unsigned** `assembleRelease` APK and uploads as artifact / Release asset
- **Does NOT use** `empire-release.jks` and must not receive that keystore as a secret

### If Eric wants signed CI builds later (HIS call)

| Secret | Meaning |
|--------|---------|
| `ANDROID_KEYSTORE_BASE64` | base64 of the jks |
| `ANDROID_KEYSTORE_PASSWORD` | keystore password |
| `ANDROID_KEY_ALIAS` | key alias (local uses `empire`) |
| `ANDROID_KEY_PASSWORD` | key password |

Then extend the APK workflow with `apksigner` — **not enabled by default**.

## iOS (INERT until Apple Developer Program)

See [IOS_CI.md](./IOS_CI.md). Workflow `ios-scaffold.yml` scaffolds only; no installable IPA without paid Apple membership + certs.
