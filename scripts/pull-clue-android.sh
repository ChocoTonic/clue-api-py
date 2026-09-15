#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
output_dir=${1:-"$project_dir/build/android/source"}
sdk_root=${ANDROID_SDK_ROOT:-/opt/homebrew/share/android-commandlinetools}
adb_bin="$sdk_root/platform-tools/adb"
package=com.clue.android

[ -x "$adb_bin" ] || { echo "adb not found: $adb_bin" >&2; exit 1; }
"$adb_bin" wait-for-device
package_paths=$("$adb_bin" shell pm path "$package" | tr -d '\r' | sed 's/^package://')
[ -n "$package_paths" ] || {
  echo "Clue is not installed from Google Play in the emulator." >&2
  exit 1
}

mkdir -p "$output_dir"
for remote_path in $package_paths; do
  local_name=$(basename "$remote_path")
  echo "Pulling $local_name..."
  "$adb_bin" pull "$remote_path" "$output_dir/$local_name"
done

echo "Extracted authorized APK set: $output_dir"
ls -1 "$output_dir"/*.apk
