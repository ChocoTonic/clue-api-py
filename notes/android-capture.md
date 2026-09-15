# Android Clue capture

This procedure reproduces the certificate-replacement approach described by
`lyczak/ClueApiDocs`. It is for an account, APK, and device that you own or are
authorized to inspect.

## What is already installed

- OpenJDK 26 from Homebrew
- apktool 3.0.3
- Android platform tools 37.0.1
- Android emulator 37.1.11
- Android API 35 Google Play ARM64 image
- Android build tools 36.1.0
- AVD: `clue-play-api35`

## 1. Start mitmproxy

```sh
# From the repository root:
./scripts/start-mitmweb.sh
```

The proxy listens on port 8080. The dashboard is
`http://127.0.0.1:8081/`.

The proxy binds to loopback by default. For an authorized physical device on a
trusted network, explicitly expose it with `MITM_LISTEN_HOST=0.0.0.0` and use
host firewall rules to limit access to that device.

## 2. Start the emulator

```sh
./scripts/start-android-emulator.sh
```

The emulator uses Android's `10.0.2.2` alias to reach the Mac.

## 3. Install and extract the official APK set

In the emulator, sign in to Google Play yourself and install Clue. Do not open
Clue or enter Clue credentials yet. The official package is `com.clue.android`.
Then extract the base and split APKs:

```sh
./scripts/pull-clue-android.sh
```

The files are placed in `build/android/source/` and ignored by Git.

## 4. Patch and sign

```sh
./scripts/patch-clue-android.sh build/android/source
```

The script:

1. Decodes the APK with apktool.
2. Detects either the historical Amazon Root CA resource or the current Android
   Network Security Config pin set.
3. Replaces the historical certificate, or removes only the `helloclue.com`
   pin set and adds the current mitmproxy CA as an app-scoped trust anchor.
4. Rebuilds and zip-aligns the APK.
5. Signs it with a local research-only key.
6. Re-signs every split with the same local key and verifies the signatures.

The output set is in `build/android/signed/`.

If neither supported pinning layout is found, the script stops without building
an APK and prints certificate-like resources for manual analysis.

## 5. Install and configure the proxy

The patched build has a different signature from the Play Store build. Remove
the original Clue installation from the emulator first if one is installed.
This deletes only the emulator's local Clue data.

```sh
./scripts/install-clue-android.sh
```

## 6. Capture

Open Clue in the emulator and sign in to your own account. In mitmweb, first
confirm that `api.helloclue.com` now produces complete HTTP flows. Capture these
actions separately:

1. App initialization.
2. Login.
3. Calendar/history loading.
4. A manual refresh with no edits.

Do not replay or modify POST, PUT, PATCH, or DELETE requests until their effects
are understood. The initial goal is to identify authentication and read-only
retrieval behavior.

## Cleanup

Disable the emulator proxy when finished:

```sh
/opt/homebrew/share/android-commandlinetools/platform-tools/adb \
  shell settings put global http_proxy :0
```
