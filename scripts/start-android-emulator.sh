#!/bin/sh
set -eu

sdk_root=${ANDROID_SDK_ROOT:-/opt/homebrew/share/android-commandlinetools}
java_home=${JAVA_HOME:-/opt/homebrew/opt/openjdk}
avd_name=${CLUE_AVD_NAME:-clue-play-api35}
emulator_bin="$sdk_root/emulator/emulator"

if [ ! -x "$emulator_bin" ]; then
  echo "Android emulator not found at $emulator_bin" >&2
  exit 1
fi

if "$sdk_root/platform-tools/adb" devices | grep -q '^emulator-.*device'; then
  echo "An Android emulator is already running."
  exit 0
fi

export ANDROID_SDK_ROOT="$sdk_root"
export JAVA_HOME="$java_home"

exec "$emulator_bin" \
  -avd "$avd_name" \
  -no-metrics \
  -no-snapshot \
  -no-boot-anim
