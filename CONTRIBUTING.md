# Contributing

Thanks for your interest. This project is small and welcoming.

## Development setup

```bash
git clone https://github.com/aousabdo/humanizer-mcp
cd humanizer-mcp
pip install -e ".[dev]"
```

Or with `uv`:

```bash
uv sync --all-extras
```

## Running the server locally

```bash
# stdio (default)
python -m humanizer_mcp

# HTTP
python -m humanizer_mcp --http --port 8000
```

## Testing

```bash
pytest
```

## Linting and formatting

```bash
ruff check .
ruff format .
```

CI runs both on every PR against Python 3.10, 3.11, 3.12, and 3.13.

## Testing against a real MCP client

The MCP Inspector is the easiest way to exercise the tools without wiring the server into Claude:

```bash
npx @modelcontextprotocol/inspector python -m humanizer_mcp
```

## Submitting changes

1. Fork, branch, commit.
2. Add a test if you touched an analysis function — they're pure and deterministic, so tests are cheap.
3. Update `CHANGELOG.md` under `[Unreleased]`.
4. Open a pull request.

## Releasing

Releases are automated. Push a tag and CI publishes to both PyPI and npm:

```bash
# bump version in src/humanizer_mcp/__init__.py and npm/package.json
git commit -am "Release 0.2.0"
git tag v0.2.0
git push origin main --tags
```

The publish workflow uses PyPI Trusted Publishing (OIDC — no API token) and an `NPM_TOKEN` repository secret.
