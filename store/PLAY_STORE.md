# Google Play submission kit — HiVE War

**Author:** Grok · **Date:** 2026-07-30 · **Order #5 Job 2**  
**Repo:** https://github.com/MiSTRFiNGA/HiveWar (renamed 2026-07-30, was HiveSwarm)  
**Web:** https://mistrfinga.github.io/HiveWar/  
**Gameplay HTML:** Claude owns `index.html` — this kit is store/compliance only.
**Note (Claude, 2026-07-30):** the product is now HiVE WAR — "HiVE SWARM" belongs to a
different, future title. The `com.empiregames.hiveswarm` package id below is intentionally
left as-is (not yet published; renaming a package id after Play submission is effectively
permanent, so that call belongs to whoever actually submits).

---

## 1. Target API level (verified)

Measured on HiVEMiND `D:\Dev\_mobile\hiveswarm\android\variables.gradle` (2026-07-30):

| Setting | Value |
|---------|-------|
| `minSdkVersion` | **24** |
| `compileSdkVersion` | **36** |
| `targetSdkVersion` | **36** |
| `applicationId` | `com.empiregames.hiveswarm` |
| `versionCode` / `versionName` | `1` / `1.0` (bump before each Play upload) |

### Play policy context

Play requires new apps/updates to target a **recent** API level (rolling yearly; API 35+ era for 2025–26). Our Capacitor projects already use **targetSdk 36** — **not a blocker**. Re-check [target API requirements](https://developer.android.com/google/play/requirements/target-sdk) the week you submit.

---

## 2. Privacy policy (Play REQUIRES a public URL)

| Item | Value |
|------|-------|
| Draft file | `privacy/index.html` |
| Intended public URL | **https://mistrfinga.github.io/HiveWar/privacy/** |
| Content | No server-side PII; localStorage only; GitHub contact |

**Eric action before Play submit:** confirm GitHub Pages serves `/privacy/` after this file is on `master`.

Without a live HTTPS privacy URL, Play Console **blocks** listing completion.

---

## 3. Data safety form (suggested answers)

| Question | Answer |
|----------|--------|
| Collect or share user data? | **No** (on-device localStorage only; no empire backend) |
| Data types | **None** declared |
| Encrypted in transit | N/A for declared collection |
| Deletion | Clear app storage / uninstall |
| Children | Not primarily directed at children |
| Independent security review | No |

If you later add Crashlytics, Firebase, or ads SDKs, revise this form before shipping.

---

## 4. Content rating questionnaire (guidance)

| Topic | Suggested |
|-------|-----------|
| Violence | Cartoon / fantasy mild |
| Sexual content | None |
| Language | None / mild UI only |
| Controlled substances | None |
| Gambling / real-money | None |
| User-to-user comms | No |
| Location | No |

Dark art (skulls / crypt) may land **Everyone 10+** or **Teen** — rate from real screenshots.

---

## 5. Listing asset SPEC (spec only — no art generated)

| Asset | Size |
|-------|------|
| App icon | **512×512** PNG |
| Feature graphic | **1024×500** |
| Phone screenshots | ≥2 (recommend 4–8), 16:9 or 9:16 within Play limits |
| 7" / 10" tablet screenshots | Optional |

### Screenshot storyboard

1. Cold-open / first playable second  
2. Core loop mid-action  
3. Progression / meta / score  
4. Peak moment  

Orientation primary: **portrait**. Genre: **Action / Auto-shooter**.

### Copy drafts

**Short (≤80 chars):**  
`HiVE War: Action / Auto-shooter. Free, offline-capable, no account.`

**Full:**

```
HiVE War is a free action / auto-shooter game from Empire Games.

• Instant play — no account required
• Lightweight Android app (offline after install)
• Progress saved on your device
• Also on the web: https://mistrfinga.github.io/HiveWar/

Privacy: https://mistrfinga.github.io/HiveWar/privacy/
```

---

## 6. Developer account

- Google Play Console: **one-time ~$25 USD** (Eric only; agents do not create accounts)
- Package name for this title: `com.empiregames.hiveswarm`

---

## 7. Review blockers / risk flags (current shell)

| Item | Risk | Notes |
|------|------|-------|
| Privacy policy URL not live yet | **BLOCKER** until Pages deploy | Draft in repo |
| CI unsigned APK | Cannot upload to Play as-is | Use local `build_apk.ps1` signed output |
| `INTERNET` permission | Low | Only permission in manifest |
| `allowBackup=true` | Low | Capacitor default |
| Target API 36 | OK | Verified |
| Ad/analytics SDKs in APK | None observed | Keep Data safety honest |
| Keystore loss | **Critical** | Losing `empire-release.jks` blocks updates for this applicationId |
| Local `build_apk.ps1` embeds keystore password | Ops risk | Keep private; **never** put in GitHub Secrets |

---

## 8. Upload checklist

1. Privacy URL live  
2. Bump versionCode/versionName  
3. `pwsh D:\Dev\_mobile\build_apk.ps1 -Game HiveSwarm -Version X.Y`  
4. Create Play app with applicationId `com.empiregames.hiveswarm`  
5. Data safety + content rating  
6. Icon / feature graphic / screenshots  
7. Internal testing → production  

## Related

- `mobile/README.md` — unsigned CI policy  
- `mobile/IOS_CI.md` — inert iOS  
- Web portal kits under `store/` where present  
