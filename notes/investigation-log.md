# Investigation log

## Current phase

Clue Android API capture and read-only Python client verification.

## Observations

Record only sanitized information here. Keep credentials, personal information,
and raw health data out of this file.

### Clue Android

- Patched Clue Android 269.1 network security configuration to trust the local
  mitmproxy certificate while preserving system trust.
- Captured authenticated requests to `api.helloclue.com`.
- Confirmed the historical `Token` authorization scheme remains current.
- Confirmed the current APK still defines `POST /access-tokens` with `email` and
  `password`, returning `access_token` and `user`.
- Replayed read-only calls directly from Python without the emulator: initialize,
  current cycle, cycle history, and measurements all returned HTTP 200.
- Isolated `Clue-Time-Zone` as the only extra header required by the tested
  date/cycle endpoints.
- Added the `clue-api-py` package with a typed client, CLI, mocked tests,
  strict type checking, and credential-safe error handling.
