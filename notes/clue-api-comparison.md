# Current Clue API compared with ClueApiDocs

Compared on 2026-09-15 using Clue Android 269.1, sanitized mitmproxy captures,
the decoded APK, and the historical `lyczak/ClueApiDocs` Swagger document.

| Area | Historical documentation | Current evidence | Result |
|---|---|---|---|
| Base URL | `https://api.helloclue.com` | Same host | Same |
| Authentication header | `Authorization: Token <token>` | Same scheme in every authenticated capture | Same |
| Email/password login | `POST /access-tokens` with `email` and `password` | Same Retrofit endpoint and JSON fields in the current APK | Contract confirmed; live login not yet replayed |
| User record | `GET /profiles/{user_id}` | `GET /users/{user_id}` observed live | Changed |
| Cycle-data download | `PATCH /sync/{user_id}` with change sets | Dedicated read endpoints under `/v1` | Replaced for current reads |
| Initialization | Not documented | `GET /v1/initialize` | New |
| Current cycle | Not documented | `GET /v1/cycles/current` | New |
| Cycle history | Not documented | `GET /v1/cycles/history` with `limit` and optional `cursor` | New |
| Measurements | Returned through sync | `GET /v1/measurements` with `start`, `end`, and optional `measurementType` | Changed |

Current cycle, history, and measurement requests return HTTP 400 without a
timezone header. `Clue-Time-Zone: <IANA name>` is sufficient; captured device,
advertising, app-version, storefront, and tracing headers are not required.

The Python client intentionally exposes the observed read endpoints directly
and returns JSON objects because this undocumented API can change without notice.
