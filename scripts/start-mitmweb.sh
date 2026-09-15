#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
mitmweb_bin="$project_dir/.venv/bin/mitmweb"
listen_host=${MITM_LISTEN_HOST:-127.0.0.1}

if [ ! -x "$mitmweb_bin" ]; then
  echo "Missing project mitmweb environment." >&2
  echo "Run: uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python mitmproxy" >&2
  exit 1
fi

exec "$mitmweb_bin" \
  --listen-host "$listen_host" \
  --listen-port 8080 \
  --web-host 127.0.0.1 \
  --web-port 8081
