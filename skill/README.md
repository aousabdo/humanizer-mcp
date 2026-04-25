# humanizer-mcp — Skill version

A standalone Claude Skill that does AI-detection scoring with no install, no server, no connector — just one file uploaded to Claude.

This is the lightweight cousin of the [humanizer-mcp](../README.md) MCP server. It's a single Markdown file that teaches Claude to score text on the same 8 signals and produce the same structured fix list. It runs entirely inside Claude's reasoning — no Python, no math library, no network call.

## Skill vs MCP server — pick the right one

| | This skill | MCP server (parent project) |
|---|---|---|
| Setup | Upload one folder to Claude | Paste a URL into Connectors *or* `pip install` |
| Determinism | Claude estimates the signals | Python computes them exactly |
| Cost | Zero infra | Free Render tier (cold-start delay) |
| Free Claude plan | No connector slot used | Uses your 1 connector |
| Best for | Casual checks, drafts, quick reads | Academic/paid work, before/after comparisons |

If a friend asks "is my draft going to flag as AI?" → skill is enough. If they're submitting it for a grade → recommend the connector.

## How to install (claude.ai)

1. Download this `humanizer-mcp/` folder. Two ways:
   - **One-click**: download the latest GitHub Release zip — it includes this folder pre-packaged. *(Coming with v0.1.2.)*
   - **Manual**: clone the repo (`git clone https://github.com/aousabdo/humanizer-mcp`), then zip the `skill/humanizer-mcp/` folder.
2. Open https://claude.ai → click your avatar → **Settings**.
3. Go to **Capabilities** (or "Skills" depending on plan).
4. Click **Upload skill** and pick the zip.
5. Done — Claude will activate the skill automatically when you ask things like *"score this for AI"* or *"check if this reads as AI-written"*.

## How to install (Claude Code)

```bash
# in any project
mkdir -p .claude/skills
cp -r path/to/humanizer-mcp .claude/skills/

# or globally for all projects
mkdir -p ~/.claude/skills
cp -r path/to/humanizer-mcp ~/.claude/skills/
```

Then start a new Claude Code session — the skill loads automatically.

## What you get

When the skill activates, Claude returns:

- A 0-100 risk score with LOW/MEDIUM/HIGH bucket.
- Which of the 8 signals fired, with evidence.
- A line-by-line fix list (specific phrases → suggested replacements).
- Structural fixes (sentence rhythm, paragraph length, voice).
- A projected score after applying the fixes.

It's the same output shape as the MCP server's `humanizer_analyze_ai_tells` tool. The numbers are estimates rather than computed — use the connector if you need defensible math.
