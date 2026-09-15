#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
apk_set=${1:-"$project_dir/build/android/signed"}
sdk_root=${ANDROID_SDK_ROOT:-/opt/homebrew/share/android-commandlinetools}
adb_bin="$sdk_root/platform-tools/adb"
proxy=${MITMPROXY_ANDROID_PROXY:-10.0.2.2:8080}

[ -x "$adb_bin" ] || { echo "adb not found: $adb_bin" >&2; exit 1; }
[ -d "$apk_set" ] || { echo "Patched APK directory not found: $apk_set" >&2; exit 1; }
[ -f "$apk_set/base.apk" ] || { echo "Patched base APK not found: $apk_set/base.apk" >&2; exit 1; }

"$adb_bin" wait-for-device
booted=$("$adb_bin" shell getprop sys.boot_completed | tr -d '\r')
[ "$booted" = 1 ] || { echo "Emulator has not finished booting." >&2; exit 1; }

echo "Configuring emulator proxy: $proxy"
"$adb_bin" shell settings put global http_proxy "$proxy"

echo "Installing patched Clue APK..."
"$adb_bin" install-multiple -r "$apk_set"/*.apk

echo "Installed package information:"
"$adb_bin" shell dumpsys package com.clue.android | \
  grep -E 'versionName=|versionCode=' | head -2
echo "Open Clue in the emulator and watch http://127.0.0.1:8081/ on the Mac."
