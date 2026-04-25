# humanizer-mcp (npm launcher)

A thin Node launcher for the Python [`humanizer-mcp`](https://pypi.org/project/humanizer-mcp/) package. Delegates to `uvx`, `pipx run`, or `python3 -m humanizer_mcp` — whichever is available on the host.

## Usage

    npx humanizer-mcp

All arguments are forwarded to the Python CLI.

## Requirements

One of the following on `PATH`:

- [`uv`](https://docs.astral.sh/uv/) (recommended — zero-install via `uvx`)
- [`pipx`](https://pipx.pypa.io/)
- `python3` with the `humanizer-mcp` package already installed (`pip install humanizer-mcp`)

## Full documentation

See the [main README](https://github.com/aousabdo/humanizer-mcp#readme) for tool descriptions, Claude client configuration, and examples.

## License

MIT
