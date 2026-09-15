# Clue API map

Only add observed endpoints. Label historical documentation explicitly.

| App | Host | Method | Path | Purpose | Authentication | Parameters | Important response fields | Read-only? | Observed test | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| Clue Android 269.1 | api.helloclue.com | POST | `/access-tokens` | Email/password login | None | JSON `email`, `password` | `access_token`, `user` (from current APK model) | No; creates token | Current APK + historical docs; not live replayed | High contract confidence |
| Clue Android 269.1 | api.helloclue.com | GET | `/v1/initialize` | Bootstrap account and feature state | `Token` | None | `actions`, `consent`, `features`, `productTier`, `subscription`, `user` | Yes | Live Python replay: 200 | High |
| Clue Android 269.1 | api.helloclue.com | GET | `/v1/cycles/current` | Current cycle and predictions | `Token` | `include-ovarian-phases`; timezone header | `analysis`, `cycle`, `dailyCategoryGroups`, `periodConfirmation` | Yes | Live Python replay: 200 | High |
| Clue Android 269.1 | api.helloclue.com | GET | `/v1/cycles/history` | Paginated cycle history | `Token` | `limit`, optional `cursor`; timezone header | `cycles`, `nextCursor` | Yes | Live Python replay: 200 | High |
| Clue Android 269.1 | api.helloclue.com | GET | `/v1/measurements` | Measurements over a date range | `Token` | `start`, `end`, optional `measurementType`; timezone header | `measurements`, `nextCursor` | Yes | Live Python replay: 200 | High |
| Clue Android 269.1 | api.helloclue.com | GET | `/v1/notifications` | Notification settings | `Token` | None | Reminder settings | Yes | App capture: 200 | High |
| Clue Android 269.1 | api.helloclue.com | GET | `/v1/wearables` | Connected wearables | `Token` | None | `wearables` | Yes | App capture: 200 | High |
| Clue Android 269.1 | api.helloclue.com | GET | `/v1/birth-control/settings` | Birth-control settings | `Token` | None | `settings` | Yes | App capture: 200 | High |
