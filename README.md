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

## Three ways to use it

| Path | Best for | What you do |
|---|---|---|
| **Hosted URL (no install, deterministic)** | claude.ai, Claude Desktop, Claude for Chrome — including Free plan | Paste one URL into *Settings → Connectors → Add custom connector*. |
| **Skill (no install, no infra, estimated)** | Same surfaces, plus people who don't want to use up their 1 free-tier connector slot | Upload the [`skill/humanizer-mcp/`](skill/humanizer-mcp/) folder under *Settings → Capabilities → Skills*. See [skill/README.md](skill/README.md). |
| **Local install (`uvx` / `npx`)** | Claude Code on the terminal, Desktop with stdio | One command in a shell. |

### Path A — add as a Custom Connector (zero install)

Works in **claude.ai (web), Claude Desktop, and Claude for Chrome** — all four surfaces share the connector list once you're signed in. Available on every plan including Free (Free is limited to one custom connector).

1. Open Claude → **Settings** → **Connectors**.
2. Click **Add custom connector**.
3. Paste the server URL (replace with your hosted instance — see [Hosting](#hosting) below):
   ```
   https://humanizer-mcp.onrender.com/mcp
   ```
4. Save. The five `humanizer_*` tools become available in any chat.

That's the whole install for non-technical users — they never touch a terminal.

### Path B — install locally (Claude Code / Desktop with stdio)

```bash
# Claude Code, one line
claude mcp add humanizer -- uvx humanizer-mcp
```

For Claude Desktop with a local stdio server, add this to `claude_desktop_config.json`:

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

Other ways to launch the local binary if you don't want `uvx`:

```bash
pip install humanizer-mcp && humanizer-mcp     # pip
npx humanizer-mcp                              # npm launcher (delegates to uvx/pipx/python3)
```

### Try it with the MCP Inspector

```bash
npx @modelcontextprotocol/inspector uvx humanizer-mcp
```

## Hosting

To create the URL in Path A, deploy the included `Dockerfile`. The repo ships with a Render Blueprint and a Fly config:

**Render** — easiest, free tier, auto-deploys from the GitHub repo:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/aousabdo/humanizer-mcp)

**Fly.io** — always-on free tier:

```bash
fly launch --copy-config --name humanizer-mcp
fly deploy
```

**Anywhere else** — the Dockerfile reads `PORT` from the environment and binds to `0.0.0.0`, so it runs on Railway, Heroku, Cloud Run, ECS, or your own box:

```bash
docker build -t humanizer-mcp .
docker run -p 8000:8000 humanizer-mcp
```

The MCP endpoint is at `/mcp` (streamable HTTP). The server is stateless and unauthenticated — anyone with the URL can call the tools, but there are no secrets and no destructive operations to abuse.

### Run the HTTP server locally

```bash
humanizer-mcp --http --port 8000
# point a client at http://127.0.0.1:8000/mcp
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
