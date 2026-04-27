# humanizer-mcp

[![PyPI version](https://img.shields.io/pypi/v/humanizer-mcp.svg)](https://pypi.org/project/humanizer-mcp/)
[![npm version](https://img.shields.io/npm/v/humanizer-mcp.svg)](https://www.npmjs.com/package/humanizer-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/humanizer-mcp.svg)](https://pypi.org/project/humanizer-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/aousabdo/humanizer-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/aousabdo/humanizer-mcp/actions/workflows/ci.yml)

An MCP (Model Context Protocol) server that measures AI-detection risk in a piece of text and tells you — line by line — what to change. Works with Claude Code, Claude Desktop, and any MCP-compatible client.

> **Just want to use it?** Go to **[aousabdo.github.io/humanizer-mcp](https://aousabdo.github.io/humanizer-mcp/)** — copy the URL, paste it into Claude's Connectors, done. The rest of this README is for developers and people self-hosting.

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

> **Sharing with non-technical users?** Two PDFs in [`share/`](share/) — email either one, no further explanation needed:
>
> - [share/humanizer-mcp-friends-guide.pdf](share/humanizer-mcp-friends-guide.pdf) — 2 pages. Truly non-technical: download a zip, upload it to Claude, done. No install.
> - [share/humanizer-mcp-boss-guide.pdf](share/humanizer-mcp-boss-guide.pdf) — 3 pages. Semi-technical Windows users who can install an app and edit a config file. Sets up the full MCP server with Claude Desktop.

### Path A — add as a Custom Connector (zero install)

Works in **claude.ai (web), Claude Desktop, and Claude for Chrome** — all four surfaces share the connector list once you're signed in. Available on every plan including Free (Free is limited to one custom connector).

A hosted reference instance is up — feel free to use it for casual evaluation:

```
https://humanizer-mcp-aousabdo.fly.dev/mcp
```

For production / privacy-sensitive use, deploy your own with the included `Dockerfile` (see [Hosting](#hosting) below — Fly.io takes ~3 minutes). The hosted instance is on a free Fly tier with no SLA, no support, and no privacy guarantees — your text passes through it.

To add it to your Claude:

1. Open Claude → **Settings** → **Connectors**.
2. Click **Add custom connector**.
3. Paste the URL above (or your own hosted instance's `/mcp` URL).
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

**Cloudflare Tunnel from your laptop** — zero hosting cost, only up while your machine is on:

```bash
brew install cloudflared
pipx install humanizer-mcp        # or: pip install humanizer-mcp
humanizer-mcp --http --port 8000 &
cloudflared tunnel --url http://localhost:8000
# copy the trycloudflare.com URL it prints
```

The MCP endpoint is at `/mcp` (streamable HTTP). The server is stateless and unauthenticated — anyone with the URL can call the tools, but there are no secrets and no destructive operations to abuse.

### Run the HTTP server locally

```bash
humanizer-mcp --http --port 8000
# point a client at http://127.0.0.1:8000/mcp
```

## Verify it works

Once installed by any path, in any Claude chat ask:

> *"What humanizer tools do you have available?"*

Claude should list five: `humanizer_analyze_ai_tells`, `humanizer_quick_vocab_scan`, `humanizer_get_rewrite_instructions`, `humanizer_compare_before_after`, `humanizer_get_banned_words`.

Then try the canonical test:

> *"Score this for AI tells: 'In today's rapidly evolving digital landscape, it's important to note that businesses must leverage cutting-edge solutions to navigate the multifaceted challenges they face.'"*

You should get a score in the HIGH bucket (≥ 60), the signals that fired, and a line-by-line fix list.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `claude mcp list` shows server but no tools | `uvx` isn't on `$PATH` for the Claude Code subprocess | `which uvx`; add `~/.local/bin` to `$PATH` in your shell rc |
| `humanizer-mcp: command not found` after `pip install` | pip user-install bin not on `$PATH` | Use `python3 -m humanizer_mcp` instead — always works |
| Claude Desktop has no hammer icon | Config JSON syntax error | `python3 -m json.tool < claude_desktop_config.json` to validate |
| `npx humanizer-mcp` hangs ~30s on first run | Launcher is shelling to `uvx`, which downloads deps on first use | Wait it out; subsequent runs are instant |
| Render-hosted: 406 spam in logs | Health Check Path is `/mcp`; should be `/health` | Settings → Health & Alerts → set to `/health` |
| Render-hosted: `pip install` killed during build | OOM on free tier (512MB) — `pydantic-core` native compile spikes | Switch to Fly free tier or upgrade Render to Starter |
| Custom Connector add fails on claude.ai Free | Already at the 1-connector limit | Remove an unused connector; or upgrade plan |

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
