#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
listen_host=${MITM_LISTEN_HOST:-127.0.0.1}

if [ -n "${MITMWEB_BIN:-}" ]; then
  mitmweb_bin=$MITMWEB_BIN
elif [ -x "$project_dir/.venv/bin/mitmweb" ]; then
  mitmweb_bin="$project_dir/.venv/bin/mitmweb"
else
  mitmweb_bin=$(command -v mitmweb || true)
fi

if [ -z "$mitmweb_bin" ] || [ ! -x "$mitmweb_bin" ]; then
  echo "mitmweb is not installed." >&2
  echo "Run: uv tool install mitmproxy" >&2
  exit 1
fi

exec "$mitmweb_bin" \
  --listen-host "$listen_host" \
  --listen-port 8080 \
  --web-host 127.0.0.1 \
  --web-port 8081
