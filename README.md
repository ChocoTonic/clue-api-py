# Clue Period Tracker API for Python

`clue-api-py` is an unofficial, read-oriented Python client for querying data
from the Clue period tracker API. It includes a typed client, CLI, and an
evidence-backed OpenAPI 3.1 contract derived from the current Android app.

This project is not affiliated with, endorsed by, or supported by Clue or
BioWink GmbH. Clue is a trademark of its respective owner.

## Safety boundary

- Use only accounts and devices you own or are explicitly authorized to test.
- Prefer observing and replaying GET/read-only requests.
- Do not replay POST, PUT, PATCH, or DELETE requests without reviewing effects.
- Raw captures, `.env`, APKs, tokens, passwords, and health data are ignored by
  Git. Do not add them with `git add -f`.

## Clue API Python client

The client was verified against Clue Android 269.1 on 2026-09-15. It uses the
current API paths observed in the app rather than treating the historical
`ClueApiDocs` Swagger file as authoritative.

Install the library from PyPI:

```console
uv add clue-api-py
```

or:

```console
python -m pip install clue-api-py
```

Install the locked development environment with UV:

```console
uv sync
uv run pytest
```

The generated [OpenAPI 3.1 contract](docs/openapi.json) records the evidence for
each endpoint as `live`, `state-dependent`, or `apk-only`. Validate or regenerate
it with:

```console
uv run python scripts/generate_openapi.py --check
uv run python scripts/generate_openapi.py
```

MITM and APK inspection tools are deliberately separate from the distributable
library:

```console
uv sync --group research
```

Log in and query in one process without storing the password or token:

```python
from getpass import getpass

from clue_api import ClueClient

email = input("Clue email: ")
with ClueClient.from_credentials(email, getpass("Clue password: ")) as clue:
    current = clue.current_cycle()
    history = clue.cycle_history(limit=20)
    measurements = clue.measurements(start="2026-01-01", end="2026-12-31")
```

The login endpoint is present in the current APK and matches the historical
contract, but the email/password flow still needs one manual live verification.
Token-authenticated reads have been verified live.

The current read-only surface includes account state, consent and notification
settings, tracking preferences, cycles and calendar data, measurements, health
analyses, wearables, birth-control metadata, connections, medical-record
options, doctor-report metadata, studies, chatbot history, paywall state, and
data-takeout credentials. See [the sanitized sweep](notes/live-read-sweep.md)
for evidence and state-dependent results.

The CLI can perform the same in-memory login and will securely prompt for the
password:

```console
read 'CLUE_EMAIL?Clue email: '
export CLUE_EMAIL
export CLUE_TIME_ZONE=America/Los_Angeles
clue-api current-cycle
unset CLUE_EMAIL
```

If you already have a token, keep it out of shell history:

```console
read -s 'CLUE_ACCESS_TOKEN?Clue token: '
export CLUE_ACCESS_TOKEN
export CLUE_TIME_ZONE=America/Los_Angeles
clue-api current-cycle
clue-api history --limit 20
clue-api measurements --start 2026-01-01 --end 2026-12-31
unset CLUE_ACCESS_TOKEN
```

Responses contain sensitive health data. Redirect output only to an encrypted,
access-controlled location.

Print the current machine-readable contract without authenticating:

```console
uv run clue-api spec > openapi.json
```

## Automation

- CI runs formatting, linting, strict typing, OpenAPI drift validation, tests on
  Python 3.11–3.14, and package builds.
- Publishing a GitHub release tagged for the package version (for example,
  `v0.2.0`) reruns those gates and publishes to PyPI through trusted publishing.
- Renovate groups Python tooling and GitHub Actions updates, maintains
  `uv.lock`, delays routine releases for five days, and requires review for
  major updates.
- Live-account tests are intentionally not run in CI; CI uses mocked HTTP and
  the sanitized contract so repository secrets are unnecessary.

## Layout

- `src/clue_api/`: typed Python client and command-line entry point.
- `docs/openapi.json`: generated evidence-backed OpenAPI 3.1 contract.
- `tests/`: mocked contract and credential-redaction tests.
- `captures/`: ignored raw mitmproxy flows kept only on this machine.
- `notes/`: sanitized observations, host inventories, and API maps.
- `examples/`: sanitized response examples only.
- `scripts/`: capture, Android patching, and sanitized inspection helpers.

See `notes/investigation-log.md` for the current research state.
