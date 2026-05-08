# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Feedback themes (2-week check-in, 2026-05-08)

- No issues or PRs opened yet as of 2026-05-08.

## [0.2.0] — 2026-04-27

### Added

- New tool `humanizer_humanize_text` that actually returns the rewritten text. Performs a deterministic mechanical pass (vocabulary swaps, AI-phrase removal, contraction injection, em-dash cleanup) and instructs the calling LLM to polish the result for context. Closes the long-standing gap where the MCP would diagnose-and-prescribe but never deliver a finished rewrite.
- `apply_mechanical_fixes()` helper that drives the rewriter — applies word-level and phrase-level substitutions from the same vocabulary the analyzer flags, plus a 30-entry contraction map and em-dash → comma cleanup.
- `humanizer_analyze_ai_tells` now also returns `mechanical_rewrite` and `mechanical_rewrite_changes` fields, so even callers that only invoke the analyzer get a real humanized starting point — not just an analysis report.

### Changed

- Tool descriptions for both analyze and humanize now include explicit `instruction_to_assistant` fields telling the calling LLM to present a polished rewrite to the user with before/after scores. This nudges Claude to always deliver an end-to-end result rather than stopping at the diagnosis.

## [0.1.1] — 2026-04-25

### Fixed

- `--http` mode now starts correctly. The previous release passed `port` to `FastMCP.run()`, which doesn't accept it, raising `TypeError` before the server could bind. Host and port now flow through `mcp.settings`, and the transport name uses the canonical `streamable-http` spelling.

### Added

- `--host` flag and `HOST` / `PORT` env vars on the CLI, so the server binds correctly under hosted runtimes (Render, Fly, etc.).
- `Dockerfile`, `render.yaml`, and `fly.toml` for one-click hosted deploys, enabling claude.ai / Claude Desktop / Claude for Chrome users to add this server as a remote Custom Connector via URL — no local install required.
- DNS-rebinding protection is disabled in HTTP mode so the server is reachable from Anthropic's connector infrastructure.

## [0.1.0] — 2026-04-24

### Added

- Initial release.
- Five MCP tools: `humanizer_analyze_ai_tells`, `humanizer_quick_vocab_scan`, `humanizer_get_rewrite_instructions`, `humanizer_compare_before_after`, `humanizer_get_banned_words`.
- Stdio and streamable-HTTP transports.
- `--version` and `--help` flags on the CLI.
- npm launcher (`humanizer-mcp`) that delegates to `uvx`, `pipx run`, or `python3 -m humanizer_mcp`.

[Unreleased]: https://github.com/aousabdo/humanizer-mcp/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/aousabdo/humanizer-mcp/releases/tag/v0.2.0
[0.1.1]: https://github.com/aousabdo/humanizer-mcp/releases/tag/v0.1.1
[0.1.0]: https://github.com/aousabdo/humanizer-mcp/releases/tag/v0.1.0
