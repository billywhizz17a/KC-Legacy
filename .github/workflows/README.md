# GitHub Actions Build Setup

## Android APK (works now — no extra setup needed)

1. Go to **Actions** tab in GitHub repo
2. Select **Build Android APK** workflow
3. Click **Run workflow**
4. Download the APK from the Artifacts section when done

## iOS IPA (requires Apple Developer Account — $99/year)

### Step 1: Get your Apple Developer credentials

1. Sign up at https://developer.apple.com/program/ ($99/year)
2. Get your **Team ID** from https://developer.apple.com/account#MembershipDetailsCard

### Step 2: Create a signing certificate

1. Go to https://developer.apple.com/account/resources/certificates/list
2. Click **+** → **Apple Development** → Continue
3. Create a Certificate Signing Request (CSR) on a Mac (Keychain Access → Certificate Assistant → Request a Certificate)
4. Upload the CSR and download the `.cer` file
5. Export it as a `.p12` file from Keychain Access (include the private key)

### Step 3: Create a provisioning profile

1. Go to https://developer.apple.com/account/resources/profiles/list
2. Click **+** → **Ad Hoc** (or **Development**) → Continue
3. Select your App ID (`com.KCLegacy.customer`)
4. Select your certificate → Continue
5. Select devices to allow → Continue
6. Name it and download the `.mobileprovision` file

### Step 4: Add secrets to GitHub

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret Name | Value |
|---|---|
| `IOS_CERTIFICATE_BASE64` | Base64-encoded `.p12` file (run `base64 -i cert.p12` on Mac/Linux) |
| `IOS_CERTIFICATE_PASSWORD` | Password you set when exporting the `.p12` |
| `IOS_PROVISIONING_PROFILE_BASE64` | Base64-encoded `.mobileprovision` file |
| `IOS_TEAM_ID` | Your Apple Team ID (e.g. `ABCDE12345`) |

### Step 5: Build

1. Go to **Actions** tab in GitHub repo
2. Select **Build iOS IPA** workflow
3. Click **Run workflow**
4. Download the IPA from the Artifacts section when done

### Without an Apple Developer Account

The workflow will still run and produce an **unsigned IPA**, but it cannot be installed on any device. You need the Apple Developer account for code signing.

## Notes

- macOS runners cost 10x more GitHub Actions minutes than Linux (1 min macOS = 10 min of your allowance)
- Free GitHub accounts get 2,000 minutes/month — that's ~200 macOS minutes
- Each iOS build takes ~10-15 minutes, so you can do ~13-20 builds/month on free tier
- The Android build runs on Linux runners (1x cost) so those are much cheaper
