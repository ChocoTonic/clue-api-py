#!/bin/sh
set -eu

usage() {
  echo "Usage: $0 /path/to/clue.apk-or-extracted-directory [output-directory]" >&2
  exit 2
}

[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage

input_path=$1
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
output_dir=${2:-"$project_dir/build/android"}
ca_pem=${MITMPROXY_CA_PEM:-"$HOME/.mitmproxy/mitmproxy-ca-cert.pem"}
sdk_root=${ANDROID_SDK_ROOT:-/opt/homebrew/share/android-commandlinetools}
build_tools=${ANDROID_BUILD_TOOLS:-36.1.0}
tool_dir="$sdk_root/build-tools/$build_tools"
apksigner="$tool_dir/apksigner"
zipalign="$tool_dir/zipalign"
export JAVA_HOME=${JAVA_HOME:-/opt/homebrew/opt/openjdk}

if [ -d "$input_path" ]; then
  input_dir=$input_path
  input_apk="$input_dir/base.apk"
else
  input_dir=
  input_apk=$input_path
fi

[ -f "$input_apk" ] || { echo "Base APK not found: $input_apk" >&2; exit 1; }
[ -f "$ca_pem" ] || { echo "mitmproxy CA not found: $ca_pem" >&2; exit 1; }
command -v apktool >/dev/null 2>&1 || { echo "apktool is required" >&2; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo "openssl is required" >&2; exit 1; }
[ -x "$apksigner" ] || { echo "apksigner not found: $apksigner" >&2; exit 1; }
[ -x "$zipalign" ] || { echo "zipalign not found: $zipalign" >&2; exit 1; }

mkdir -p "$output_dir"
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/clue-apk.XXXXXX")
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM
decoded_dir="$work_dir/decoded"
unsigned_apk="$work_dir/clue-mitm-unsigned.apk"
aligned_apk="$work_dir/clue-mitm-aligned.apk"
signed_dir="$output_dir/signed"
output_apk="$signed_dir/base.apk"
debug_keystore="$output_dir/clue-debug.keystore"
mkdir -p "$signed_dir"

echo "Decoding $(basename "$input_apk")..."
apktool decode --force --output "$decoded_dir" "$input_apk"

pin_list="$work_dir/pins.txt"
find "$decoded_dir" -type f \( \
  -iname '*amazon*root*ca1*' -o \
  -iname '*amazon_root_ca_1*' \
\) -print > "$pin_list"
pin_count=$(wc -l < "$pin_list" | tr -d ' ')
network_config="$decoded_dir/res/xml/network_security_config.xml"

if [ "$pin_count" -eq 1 ]; then
  pin_path=$(sed -n '1p' "$pin_list")
  echo "Replacing historical bundled pin: ${pin_path#"$decoded_dir"/}"
  openssl x509 -in "$ca_pem" -outform DER -out "$pin_path"
elif [ "$pin_count" -eq 0 ] && [ -f "$network_config" ] && grep -q '<pin-set>' "$network_config"; then
  echo "Replacing current helloclue.com pin-set with an app-scoped mitmproxy trust anchor..."
  mkdir -p "$decoded_dir/res/raw"
  openssl x509 -in "$ca_pem" -outform DER \
    -out "$decoded_dir/res/raw/mitmproxy_ca.cer"
  patched_config="$work_dir/network_security_config.xml"
  awk '
    !done && /<pin-set>/ { in_pin = 1; next }
    in_pin && /<\/pin-set>/ {
      in_pin = 0
      print "        <trust-anchors>"
      print "            <certificates src=\"system\" />"
      print "            <certificates src=\"@raw/mitmproxy_ca\" />"
      print "        </trust-anchors>"
      done = 1
      next
    }
    !in_pin { print }
    END { if (!done) exit 2 }
  ' "$network_config" > "$patched_config"
  cp "$patched_config" "$network_config"
else
  echo "No supported Clue certificate-pinning layout was found." >&2
  echo "Certificate-like resources found:" >&2
  find "$decoded_dir/res" "$decoded_dir/assets" -type f \( \
    -iname '*cert*' -o -iname '*.cer' -o -iname '*.crt' -o \
    -iname '*.der' -o -iname '*.pem' -o -iname '*root*ca*' \
  \) -print 2>/dev/null >&2 || true
  echo "No APK was rebuilt." >&2
  exit 1
fi

echo "Rebuilding APK..."
apktool build "$decoded_dir" --output "$unsigned_apk"
"$zipalign" -f -p 4 "$unsigned_apk" "$aligned_apk"

if [ ! -f "$debug_keystore" ]; then
  echo "Creating a local research-only signing key..."
  "$JAVA_HOME/bin/keytool" -genkeypair \
    -keystore "$debug_keystore" \
    -storepass android \
    -keypass android \
    -alias clue-research \
    -keyalg RSA \
    -keysize 2048 \
    -validity 3650 \
    -dname 'CN=Clue API Research,OU=Local Testing,O=Local,C=US' >/dev/null
fi

echo "Signing APK..."
"$apksigner" sign \
  --ks "$debug_keystore" \
  --ks-key-alias clue-research \
  --ks-pass pass:android \
  --key-pass pass:android \
  --out "$output_apk" \
  "$aligned_apk"
"$apksigner" verify --verbose "$output_apk"

if [ -n "$input_dir" ]; then
  for split_apk in "$input_dir"/split*.apk; do
    [ -f "$split_apk" ] || continue
    split_name=$(basename "$split_apk")
    aligned_split="$work_dir/aligned-$split_name"
    signed_split="$signed_dir/$split_name"
    "$zipalign" -f -p 4 "$split_apk" "$aligned_split"
    "$apksigner" sign \
      --ks "$debug_keystore" \
      --ks-key-alias clue-research \
      --ks-pass pass:android \
      --key-pass pass:android \
      --out "$signed_split" \
      "$aligned_split"
    "$apksigner" verify "$signed_split"
  done
fi

echo "Patched APK set: $signed_dir"
echo "SHA-256: $(shasum -a 256 "$output_apk" | awk '{print $1}')"
