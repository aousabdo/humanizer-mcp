# Shareable assets

Polished, ready-to-send guides for non-technical and semi-technical users. Email-attachment friendly.

## What's here

| File | For | What it is |
|---|---|---|
| [`humanizer-mcp-boss-guide.pdf`](humanizer-mcp-boss-guide.pdf) | Semi-technical Windows users (executives, managers, anyone who can install apps and edit a config file) | 3-page Windows-first walkthrough — installs the `uv` launcher, edits `claude_desktop_config.json`, restarts Claude Desktop. Includes troubleshooting. |
| [`humanizer-mcp-boss-guide.html`](humanizer-mcp-boss-guide.html) | Source for the PDF above | Self-contained HTML with print styles. Edit and re-render via `weasyprint humanizer-mcp-boss-guide.html humanizer-mcp-boss-guide.pdf`. |

## Direct download links

- **PDF**: https://github.com/aousabdo/humanizer-mcp/raw/main/share/humanizer-mcp-boss-guide.pdf
- **HTML preview**: https://htmlpreview.github.io/?https://github.com/aousabdo/humanizer-mcp/blob/main/share/humanizer-mcp-boss-guide.html

## Distribution paths matrix

For non-technical and casual users, also see [`../skill/`](../skill/) — a one-file Claude Skill that runs without any install or hosted infrastructure.

| Audience | Best asset |
|---|---|
| Boss / executive on Windows, has Claude Desktop | This PDF |
| Friend who'll never install Python, just wants a quick check | The skill at [`../skill/humanizer-mcp.zip`](../skill/humanizer-mcp.zip) |
| Developer | The main [README](../README.md) |
| Someone with a paid claude.ai plan who'd rather paste a URL | The Custom Connector path in the main README |

## Re-rendering the PDF

After editing the HTML:

```bash
weasyprint share/humanizer-mcp-boss-guide.html share/humanizer-mcp-boss-guide.pdf
```

`weasyprint` is the cleanest renderer for this layout. `wkhtmltopdf` and Chrome headless also work but produce different spacing and font rendering.
