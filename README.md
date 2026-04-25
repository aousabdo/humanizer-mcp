# humanizer-mcp

[![PyPI version](https://img.shields.io/pypi/v/humanizer-mcp.svg)](https://pypi.org/project/humanizer-mcp/)
[![npm version](https://img.shields.io/npm/v/humanizer-mcp.svg)](https://www.npmjs.com/package/humanizer-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/humanizer-mcp.svg)](https://pypi.org/project/humanizer-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/aousabdo/humanizer-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/aousabdo/humanizer-mcp/actions/workflows/ci.yml)

An MCP (Model Context Protocol) server that measures AI-detection risk in a piece of text and tells you — line by line — what to change. Works with Claude Code, Claude Desktop, and any MCP-compatible client.

Rather than running your prose through a black-box "humanizer," this server analyzes it against known detection signals (vocabulary, burstiness, contraction usage, paragraph uniformity, em dashes, first-person voice) and returns a structured report with a 0–100 risk score and a concrete rewrite plan. The actual rewriting is left to the LLM that's driving the conversation — which is the point: a planner, not a laundering service.

## Tools

| Tool | What it does |
|---|---|
| `humanizer_analyze_ai_tells` | Full analysis with risk score and fix recommendations. |
| `humanizer_quick_vocab_scan` | Fast word- and phrase-level scan with replacement suggestions. |
| `humanizer_get_rewrite_instructions` | Step-by-step rewrite plan, tailored to text type (blog / business / academic / email / general). |
| `humanizer_compare_before_after` | Side-by-side metrics for an original and a rewrite, with a PASS / IMPROVED / NEEDS MORE WORK verdict. |
| `humanizer_get_banned_words` | The full vocabulary and phrase ban list, for reference. |

## Installation

### With `uvx` (recommended — no install step)

```bash
uvx humanizer-mcp
```

### With `pip`

```bash
pip install humanizer-mcp
humanizer-mcp
```

### With `npx`

```bash
npx humanizer-mcp
```

The npm package is a thin launcher that delegates to `uvx`, `pipx run`, or `python3 -m humanizer_mcp` — whichever is available on the host.

## Configure your MCP client

### Claude Code

```bash
claude mcp add humanizer -- uvx humanizer-mcp
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "humanizer": {
      "command": "uvx",
      "args": ["humanizer-mcp"]
    }
  }
}
```

Config location:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### Generic MCP client (stdio)

```json
{
  "command": "uvx",
  "args": ["humanizer-mcp"]
}
```

### HTTP transport

For remote access, run the server on a port and point your client at it:

```bash
humanizer-mcp --http --port 8000
```

## Try it with the MCP Inspector

Poke at the tools without configuring a client:

```bash
npx @modelcontextprotocol/inspector uvx humanizer-mcp
```

## Example prompts

With the server connected to Claude, you can say things like:

- *"Analyze this blog post for AI tells and tell me what to change."*
- *"Run a quick vocab scan on this paragraph."*
- *"Give me rewrite instructions for this academic abstract — keep it formal but fix the burstiness."*
- *"Compare these two drafts. Did my edit actually lower the detection risk?"*

Claude picks the right tool automatically.

## How the risk score works

The 0–100 score combines eight signals:

1. **AI vocabulary hits** — words statistically overrepresented in LLM output (`delve`, `crucial`, `leverage`, `myriad`, …).
2. **AI phrase hits** — cliché structural tells (`it's important to note`, `in the ever-evolving`, `at the end of the day`, …).
3. **Burstiness** — coefficient of variation of sentence lengths. AI writing clusters around a single length; humans mix short fragments and long digressions.
4. **Contractions** — expanded forms (*it is*, *do not*) read as AI-formal; contractions read as conversational.
5. **Paragraph uniformity** — AI tends to produce paragraphs of similar size.
6. **Rhetorical questions** — near-absent in AI prose above 200 words.
7. **First-person voice** — AI avoids *I*, *we*, *my*, *our* unless prompted.
8. **Em dashes** — a ChatGPT signature; heavy use is a strong signal.

Each signal adds to the score independently; the total is clamped to 100 and bucketed into LOW (≤ 20), MEDIUM (21–50), or HIGH (51+).

## Development

```bash
git clone https://github.com/aousabdo/humanizer-mcp
cd humanizer-mcp
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more.

## License

MIT — see [LICENSE](LICENSE).
