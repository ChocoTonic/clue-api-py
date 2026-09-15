# Contributing

## Development

```console
uv sync
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
uv run python scripts/generate_openapi.py --check
uv build
```

To work with local APKs and mitmproxy captures, install the isolated research
tooling as well:

```console
uv tool install mitmproxy
```

Never commit captures, credentials, access tokens, APKs, or real health data.

## Contract evidence

Each endpoint in `src/clue_api/contracts.py` must be labeled as one of:

- `live`: returned a successful response in a sanitized read-only replay.
- `state-dependent`: declared by the app but returned a state-specific response,
  such as 404 for an account that is not pregnant.
- `apk-only`: declared by the current APK but not replayed successfully.

After changing the endpoint inventory, regenerate the checked-in OAS document:

```console
uv run python scripts/generate_openapi.py
```

The CI check fails if the generated document is stale or invalid.

## Release

1. Update the version in `pyproject.toml` and `src/clue_api/_version.py`.
2. Run the development checks above and commit the result.
3. Create a GitHub release with a matching `vX.Y.Z` tag.

The release workflow verifies that the tag matches the package version, reruns
all quality gates, builds the distributions, and publishes them through PyPI
Trusted Publishing. Do not upload distributions manually.
