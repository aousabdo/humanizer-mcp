"""
humanizer_mcp.server — FastMCP server implementation.

Provides tools for analyzing AI tells in text, humanizing AI-generated content,
and checking text against detection patterns. Works with Claude.ai, Claude Code,
and any MCP-compatible client.

Usage (stdio, local):
    humanizer-mcp

Usage (HTTP, remote):
    humanizer-mcp --http --port 8000
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from enum import Enum
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, ConfigDict, Field

# ─────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────

SERVER_NAME = "humanizer_mcp"

# Words statistically overrepresented in AI-generated text
AI_VOCABULARY: dict[str, list[str]] = {
    "delve": ["dig into", "explore", "look at", "examine"],
    "crucial": ["important", "key", "big", "necessary"],
    "landscape": ["field", "space", "world", "scene"],
    "leverage": ["use", "apply", "tap into", "lean on"],
    "multifaceted": ["complex", "layered", "varied"],
    "comprehensive": ["thorough", "full", "complete", "detailed"],
    "facilitate": ["help", "enable", "make possible", "let"],
    "streamline": ["simplify", "speed up", "cut down"],
    "moreover": [""],  # delete entirely
    "furthermore": [""],
    "additionally": ["also", "plus", "and"],
    "harness": ["use", "tap", "put to work"],
    "underscore": ["highlight", "show", "prove", "point to"],
    "navigate": ["handle", "work through", "deal with"],
    "illuminate": ["show", "reveal", "clarify", "explain"],
    "embark": ["start", "begin", "kick off"],
    "foster": ["build", "grow", "support", "encourage"],
    "endeavor": ["effort", "attempt", "try", "project"],
    "tapestry": ["mix", "blend", "web", "collection"],
    "showcase": ["show", "display", "demonstrate"],
    "pivotal": ["key", "turning-point", "defining"],
    "bolster": ["strengthen", "support", "boost", "back up"],
    "nuanced": ["subtle", "detailed", "fine-grained"],
    "robust": ["strong", "solid", "reliable"],
    "paradigm": ["model", "framework", "approach", "way"],
    "synergy": ["teamwork", "combined effect", "collaboration"],
    "holistic": ["complete", "full-picture", "overall"],
    "myriad": ["many", "a range of", "lots of", "plenty of"],
    "plethora": ["many", "a lot of", "plenty of"],
    "juxtaposition": ["contrast", "comparison", "side-by-side"],
    "arguably": [""],  # delete — take a position instead
}

# Phrases that are AI structural tells
AI_PHRASES: list[str] = [
    "it's important to note",
    "it's worth noting",
    "it is important to note",
    "it is worth noting",
    "in conclusion",
    "in today's rapidly evolving",
    "in today's fast-paced",
    "in the ever-evolving",
    "in the realm of",
    "at its core",
    "plays a crucial role",
    "plays a pivotal role",
    "it's not just",
    "it is not just",
    "stands as a testament",
    "serves as a reminder",
    "remains to be seen",
    "only time will tell",
    "the question remains",
    "as we move forward",
    "looking ahead",
    "going forward",
    "the bottom line is",
    "when it comes to",
    "at the end of the day",
    "whether you're a",
    "from seasoned professionals to",
    "both seasoned and",
    "let's dive in",
    "without further ado",
    "buckle up",
]

# ─────────────────────────────────────────────────────────────────────
# Server Setup
# ─────────────────────────────────────────────────────────────────────

mcp = FastMCP(SERVER_NAME)


# ─────────────────────────────────────────────────────────────────────
# Landing Page (HTTP only) — visited at the root URL when hosted
# ─────────────────────────────────────────────────────────────────────

_LANDING_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Humanizer MCP — add to Claude</title>
<meta name="description" content="A Claude tool that scores text for AI-detection risk and tells you what to fix. Add it to Claude in 30 seconds.">
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body {
    font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    max-width: 680px; margin: 0 auto; padding: 32px 20px 80px;
    color: #1a1a1a; background: #fafaf7;
  }
  @media (prefers-color-scheme: dark) {
    body { color: #e8e6e1; background: #1a1a1a; }
    .url-box { background: #2a2a2a; border-color: #444; }
    .step { border-color: #333; }
    code { background: #2a2a2a; }
  }
  h1 { font-size: 28px; margin: 0 0 8px; letter-spacing: -0.02em; }
  .tagline { color: #666; margin: 0 0 32px; }
  @media (prefers-color-scheme: dark) { .tagline { color: #aaa; } }
  h2 { font-size: 18px; margin: 32px 0 12px; }
  .url-box {
    display: flex; gap: 8px; align-items: stretch;
    border: 1px solid #ddd; border-radius: 8px; padding: 4px;
    background: #fff; margin: 8px 0 24px;
  }
  .url-box input {
    flex: 1; border: 0; outline: 0; background: transparent;
    font: 14px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
    padding: 10px 12px; color: inherit; min-width: 0;
  }
  .url-box button {
    border: 0; border-radius: 6px; padding: 10px 16px; cursor: pointer;
    background: #1a1a1a; color: #fff; font: inherit; font-weight: 500;
    transition: background 0.15s;
  }
  .url-box button:hover { background: #333; }
  .url-box button.copied { background: #2d8659; }
  @media (prefers-color-scheme: dark) {
    .url-box button { background: #e8e6e1; color: #1a1a1a; }
    .url-box button:hover { background: #fff; }
  }
  ol { padding-left: 20px; }
  ol li { margin: 6px 0; }
  .step { border-left: 3px solid #ddd; padding: 12px 16px; margin: 12px 0; border-radius: 4px; }
  code {
    font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
    background: #f0ede6; padding: 2px 6px; border-radius: 4px;
  }
  pre {
    font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
    background: #1a1a1a; color: #e8e6e1; padding: 12px; border-radius: 6px;
    overflow-x: auto; margin: 8px 0;
  }
  pre code {
    background: transparent;
    padding: 0;
    color: inherit;
    font-size: inherit;
  }
  details { margin: 24px 0; }
  details summary { cursor: pointer; font-weight: 500; padding: 8px 0; }
  .footer { margin-top: 48px; color: #888; font-size: 14px; }
  .footer a { color: inherit; }
  .small { font-size: 14px; color: #888; }
</style>
</head>
<body>
  <h1>Humanizer MCP</h1>
  <p class="tagline">Scores your text for AI-detection risk and tells you what to fix — line by line. Adds five tools to Claude in about 30 seconds.</p>

  <h2>1. Copy this URL</h2>
  <div class="url-box">
    <input id="url" readonly value="__BASE_URL__/mcp">
    <button id="copy-btn" onclick="copyUrl()">Copy</button>
  </div>

  <h2>2. Add it to Claude</h2>
  <p>Works in <strong>claude.ai (web)</strong>, <strong>Claude Desktop</strong>, and <strong>Claude for Chrome</strong>. You only set it up once — adding it on any one of those automatically makes it available in all three.</p>
  <div class="step">
    <ol>
      <li>Open Claude (any of the surfaces above).</li>
      <li>Go to <strong>Settings</strong> → <strong>Connectors</strong>.</li>
      <li>Click <strong>Add custom connector</strong>.</li>
      <li>Paste the URL into the <em>Remote MCP server URL</em> field.</li>
      <li>Click <strong>Add</strong> or <strong>Save</strong>.</li>
    </ol>
    <p class="small">Free Claude plans are limited to one custom connector. Pro/Max/Team/Enterprise have no limit.</p>
  </div>

  <h2>3. Use it</h2>
  <p>In any Claude chat, paste your text and try one of these:</p>
  <ul>
    <li><em>"Analyze this for AI tells and tell me what to change."</em></li>
    <li><em>"Run a quick vocab scan on this paragraph."</em></li>
    <li><em>"Compare these two drafts. Did my edit lower the AI-detection risk?"</em></li>
  </ul>
  <p>Claude picks the right tool automatically.</p>

  <details>
    <summary>For developers — install locally instead</summary>
    <p>If you'd rather run the server on your own machine (faster, fully private, works offline once installed):</p>
    <p><strong>Claude Code:</strong></p>
    <pre><code>claude mcp add humanizer -- uvx humanizer-mcp</code></pre>
    <p><strong>Claude Desktop</strong> — add to <code>claude_desktop_config.json</code>:</p>
    <pre><code>{
  "mcpServers": {
    "humanizer": {
      "command": "uvx",
      "args": ["humanizer-mcp"]
    }
  }
}</code></pre>
  </details>

  <p class="footer">
    Source &amp; docs: <a href="https://github.com/aousabdo/humanizer-mcp">github.com/aousabdo/humanizer-mcp</a>
    · MIT licensed
    · <a href="https://pypi.org/project/humanizer-mcp/">PyPI</a>
    · <a href="https://www.npmjs.com/package/humanizer-mcp">npm</a>
  </p>

<script>
  function copyUrl() {
    const input = document.getElementById('url');
    const btn = document.getElementById('copy-btn');
    input.select();
    navigator.clipboard.writeText(input.value).then(() => {
      btn.textContent = 'Copied';
      btn.classList.add('copied');
      setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1600);
    });
  }
</script>
</body>
</html>"""


@mcp.custom_route("/", methods=["GET"])
async def landing_page(request):  # type: ignore[no-untyped-def]
    """Friendly landing page so non-technical users get instructions, not a 404."""
    from starlette.responses import HTMLResponse

    # Honor the proxy headers: Fly/Render/etc. terminate TLS at the edge and
    # forward plain HTTP to the container, so request.url.scheme is "http"
    # even when the user is on HTTPS. Anthropic's Custom Connector form
    # rejects http:// URLs, so we must advertise the public scheme.
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", request.url.hostname or "localhost")
    base_url = f"{proto}://{host}"
    return HTMLResponse(_LANDING_HTML.replace("__BASE_URL__", base_url))


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):  # type: ignore[no-untyped-def]
    """Simple liveness probe for hosted deployments."""
    from starlette.responses import JSONResponse

    return JSONResponse({"status": "ok", "service": SERVER_NAME})


# ─────────────────────────────────────────────────────────────────────
# Shared Utilities
# ─────────────────────────────────────────────────────────────────────


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, handling common abbreviations."""
    text = re.sub(r"(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|etc|e\.g|i\.e)\.", r"\1<PERIOD>", text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.replace("<PERIOD>", ".").strip() for s in sentences if s.strip()]


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def sentence_lengths(text: str) -> list[int]:
    """Get word count for each sentence."""
    return [count_words(s) for s in split_sentences(text)]


def calculate_burstiness(lengths: list[int]) -> float:
    """Calculate burstiness as coefficient of variation of sentence lengths.

    Higher = more human-like variation. AI typically < 0.3, humans > 0.5.
    """
    if len(lengths) < 2:
        return 0.0
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.0
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    std_dev = math.sqrt(variance)
    return round(std_dev / mean, 3)


def find_ai_vocabulary(text: str) -> list[dict[str, Any]]:
    """Find AI-associated words in text with positions and suggestions."""
    findings: list[dict[str, Any]] = []
    text_lower = text.lower()
    for word, replacements in AI_VOCABULARY.items():
        pattern = r"\b" + re.escape(word) + r"\b"
        for match in re.finditer(pattern, text_lower):
            findings.append(
                {
                    "word": word,
                    "position": match.start(),
                    "context": text[max(0, match.start() - 30) : match.end() + 30],
                    "replacements": [r for r in replacements if r],
                }
            )
    return findings


def find_ai_phrases(text: str) -> list[dict[str, Any]]:
    """Find AI-associated phrases in text."""
    findings: list[dict[str, Any]] = []
    text_lower = text.lower()
    for phrase in AI_PHRASES:
        idx = text_lower.find(phrase)
        while idx != -1:
            findings.append(
                {
                    "phrase": phrase,
                    "position": idx,
                    "context": text[max(0, idx - 20) : idx + len(phrase) + 20],
                }
            )
            idx = text_lower.find(phrase, idx + 1)
    return findings


def count_em_dashes(text: str) -> int:
    """Count em dashes (— and --)."""
    return text.count("—") + text.count(" -- ") + text.count(" - ")


def check_contraction_usage(text: str) -> dict[str, Any]:
    """Check if text uses contractions (human) or expanded forms (AI)."""
    contractions = [
        "don't",
        "doesn't",
        "won't",
        "can't",
        "isn't",
        "aren't",
        "wasn't",
        "weren't",
        "hasn't",
        "haven't",
        "hadn't",
        "wouldn't",
        "couldn't",
        "shouldn't",
        "it's",
        "that's",
        "there's",
        "here's",
        "what's",
        "who's",
        "let's",
        "we're",
        "they're",
        "you're",
        "I'm",
        "he's",
        "she's",
        "we've",
        "they've",
        "you've",
        "I've",
        "we'd",
        "they'd",
        "you'd",
        "I'd",
        "he'd",
        "she'd",
        "we'll",
        "they'll",
        "you'll",
        "I'll",
        "he'll",
        "she'll",
    ]

    expanded = [
        "do not",
        "does not",
        "will not",
        "cannot",
        "is not",
        "are not",
        "was not",
        "were not",
        "has not",
        "have not",
        "had not",
        "would not",
        "could not",
        "should not",
        "it is",
        "that is",
        "there is",
        "here is",
        "what is",
        "who is",
        "let us",
        "we are",
        "they are",
        "you are",
        "I am",
        "he is",
        "she is",
        "we have",
        "they have",
        "you have",
        "I have",
        "we would",
        "they would",
        "you would",
        "I would",
        "he would",
        "she would",
        "we will",
        "they will",
        "you will",
        "I will",
        "he will",
        "she will",
    ]

    text_lower = text.lower()
    contraction_count = sum(1 for c in contractions if c in text_lower)
    expanded_count = sum(1 for e in expanded if f" {e} " in f" {text_lower} ")

    return {
        "contractions_found": contraction_count,
        "expanded_forms_found": expanded_count,
        "ratio": round(contraction_count / max(expanded_count, 1), 2),
        "assessment": "human-like"
        if contraction_count > expanded_count
        else "AI-like (too formal)",
    }


def check_paragraph_uniformity(text: str) -> dict[str, Any]:
    """Analyze paragraph length variation."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) < 2:
        return {"paragraph_count": len(paragraphs), "uniformity": "insufficient data"}

    lengths = [count_words(p) for p in paragraphs]
    mean = sum(lengths) / len(lengths)
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    cv = math.sqrt(variance) / mean if mean > 0 else 0

    return {
        "paragraph_count": len(paragraphs),
        "lengths": lengths,
        "mean_length": round(mean, 1),
        "coefficient_of_variation": round(cv, 3),
        "assessment": "good variation" if cv > 0.4 else "too uniform (AI-like)",
    }


def check_rhetorical_questions(text: str) -> int:
    """Count rhetorical questions (sentences ending with ?)."""
    sentences = split_sentences(text)
    return sum(1 for s in sentences if s.strip().endswith("?"))


def check_first_person(text: str) -> dict[str, Any]:
    """Check for first-person usage which signals human authorship."""
    first_person = [
        "I ",
        "I'm",
        "I've",
        "I'd",
        "my ",
        "mine ",
        "me ",
        "we ",
        "we're",
        "we've",
        "we'd",
        "our ",
        "ours ",
        "us ",
    ]
    text_check = f" {text} "
    found = [fp.strip() for fp in first_person if fp in text_check]
    count = sum(text_check.lower().count(fp.lower()) for fp in first_person)
    return {
        "first_person_markers": found,
        "total_occurrences": count,
        "assessment": "good - human voice present"
        if count >= 3
        else "weak - add personal perspective",
    }


def compute_risk_score(analysis: dict[str, Any]) -> dict[str, Any]:
    """Compute an overall AI detection risk score from analysis results."""
    score = 0  # 0 = no risk, 100 = definitely flagged
    reasons: list[str] = []

    vocab_count = analysis.get("ai_vocabulary_count", 0)
    if vocab_count >= 5:
        score += 25
        reasons.append(f"{vocab_count} AI-associated words found")
    elif vocab_count >= 2:
        score += 10
        reasons.append(f"{vocab_count} AI-associated words found")

    phrase_count = analysis.get("ai_phrase_count", 0)
    if phrase_count >= 3:
        score += 20
        reasons.append(f"{phrase_count} AI-associated phrases found")
    elif phrase_count >= 1:
        score += 10
        reasons.append(f"{phrase_count} AI-associated phrases found")

    burstiness = analysis.get("burstiness", 0)
    if burstiness < 0.25:
        score += 20
        reasons.append(f"Low burstiness ({burstiness}) — sentences too uniform")
    elif burstiness < 0.35:
        score += 10
        reasons.append(f"Moderate burstiness ({burstiness}) — could use more variation")

    contraction_data = analysis.get("contractions", {})
    if contraction_data.get("assessment") == "AI-like (too formal)":
        score += 10
        reasons.append("Too few contractions — reads formal/AI-like")

    para_data = analysis.get("paragraph_uniformity", {})
    if para_data.get("assessment") == "too uniform (AI-like)":
        score += 10
        reasons.append("Paragraph lengths too uniform")

    rq_count = analysis.get("rhetorical_questions", 0)
    word_count = analysis.get("word_count", 0)
    if word_count > 200 and rq_count == 0:
        score += 5
        reasons.append("No rhetorical questions in a long piece")

    fp_data = analysis.get("first_person", {})
    if "weak" in fp_data.get("assessment", ""):
        score += 5
        reasons.append("Little first-person voice")

    em_dash_count = analysis.get("em_dash_count", 0)
    if em_dash_count >= 5:
        score += 5
        reasons.append(f"{em_dash_count} em dashes — ChatGPT signature")

    score = min(score, 100)

    if score <= 20:
        risk_level = "LOW"
    elif score <= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "factors": reasons,
    }


# ─────────────────────────────────────────────────────────────────────
# Input Models
# ─────────────────────────────────────────────────────────────────────


class AnalyzeTextInput(BaseModel):
    """Input for analyzing text for AI tells."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: str = Field(
        ...,
        description="The text to analyze for AI-generated patterns. Paste the full content.",
        min_length=20,
        max_length=50000,
    )


class TextType(str, Enum):
    """Type of text being humanized, affects rewriting aggressiveness."""

    BLOG = "blog"
    BUSINESS = "business"
    ACADEMIC = "academic"
    EMAIL = "email"
    GENERAL = "general"


class HumanizeTextInput(BaseModel):
    """Input for humanizing AI-generated text."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: str = Field(
        ...,
        description="The AI-generated text to humanize.",
        min_length=20,
        max_length=50000,
    )
    text_type: TextType = Field(
        default=TextType.GENERAL,
        description="Type of text: 'blog', 'business', 'academic', 'email', or 'general'. Affects rewriting intensity.",
    )
    preserve_meaning: bool = Field(
        default=True,
        description="If true, preserve the core meaning and facts. If false, allow more creative liberties.",
    )
    voice_notes: str | None = Field(
        default=None,
        description="Optional notes about desired voice/style, e.g. 'conversational and slightly sarcastic' or 'authoritative but accessible'.",
        max_length=500,
    )


class VocabCheckInput(BaseModel):
    """Input for quick vocabulary-only scan."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: str = Field(
        ...,
        description="Text to scan for AI-associated vocabulary.",
        min_length=10,
        max_length=50000,
    )


class RewriteSectionInput(BaseModel):
    """Input for rewriting a specific section/paragraph."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: str = Field(
        ...,
        description="The specific paragraph or section to rewrite.",
        min_length=10,
        max_length=10000,
    )
    context: str | None = Field(
        default=None,
        description="Surrounding context (what comes before/after) to maintain coherence.",
        max_length=5000,
    )
    instruction: str | None = Field(
        default=None,
        description="Specific rewriting instruction, e.g. 'make more conversational' or 'add a personal anecdote'.",
        max_length=500,
    )


# ─────────────────────────────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────────────────────────────


@mcp.tool(
    name="humanizer_analyze_ai_tells",
    annotations={
        "title": "Analyze Text for AI Tells",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def analyze_ai_tells(params: AnalyzeTextInput) -> str:
    """Analyze text for AI-generated patterns and compute a detection risk score.

    Scans for AI-associated vocabulary, structural patterns, burstiness,
    contraction usage, paragraph uniformity, rhetorical questions, first-person
    voice, and em dash frequency. Returns a comprehensive report with a 0–100
    risk score and specific recommendations.

    Args:
        params (AnalyzeTextInput): Contains the text to analyze.

    Returns:
        str: JSON report with risk score, detected patterns, and fix recommendations.
    """
    text = params.text

    vocab_findings = find_ai_vocabulary(text)
    phrase_findings = find_ai_phrases(text)
    sent_lengths = sentence_lengths(text)
    burstiness = calculate_burstiness(sent_lengths)
    contractions = check_contraction_usage(text)
    para_uniformity = check_paragraph_uniformity(text)
    rq_count = check_rhetorical_questions(text)
    first_person = check_first_person(text)
    em_dashes = count_em_dashes(text)
    word_count = count_words(text)

    analysis: dict[str, Any] = {
        "word_count": word_count,
        "sentence_count": len(sent_lengths),
        "ai_vocabulary_count": len(vocab_findings),
        "ai_vocabulary": vocab_findings[:20],
        "ai_phrase_count": len(phrase_findings),
        "ai_phrases": phrase_findings[:10],
        "sentence_lengths": sent_lengths,
        "burstiness": burstiness,
        "contractions": contractions,
        "paragraph_uniformity": para_uniformity,
        "rhetorical_questions": rq_count,
        "first_person": first_person,
        "em_dash_count": em_dashes,
    }

    risk = compute_risk_score(analysis)
    analysis["risk_assessment"] = risk

    recommendations: list[str] = []
    if len(vocab_findings) > 0:
        top_words = list({v["word"] for v in vocab_findings})[:5]
        recommendations.append(f"Replace AI vocabulary: {', '.join(top_words)}")
    if len(phrase_findings) > 0:
        recommendations.append("Remove or rephrase AI-associated phrases")
    if burstiness < 0.35:
        recommendations.append(
            "Vary sentence lengths more aggressively (mix 4-word and 30-word sentences)"
        )
    if contractions.get("assessment") == "AI-like (too formal)":
        recommendations.append("Add contractions (don't, it's, we've, etc.)")
    if para_uniformity.get("assessment") == "too uniform (AI-like)":
        recommendations.append("Create paragraph length asymmetry (1-sentence + 8-sentence mix)")
    if word_count > 200 and rq_count == 0:
        recommendations.append("Add 1-2 rhetorical questions")
    if "weak" in first_person.get("assessment", ""):
        recommendations.append("Add first-person perspective (I, we, my, our)")
    if em_dashes >= 5:
        recommendations.append(
            f"Reduce em dashes from {em_dashes} to 1-2 (replace with commas/periods)"
        )

    analysis["recommendations"] = recommendations

    return json.dumps(analysis, indent=2)


@mcp.tool(
    name="humanizer_quick_vocab_scan",
    annotations={
        "title": "Quick AI Vocabulary Scan",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def quick_vocab_scan(params: VocabCheckInput) -> str:
    """Fast scan for AI-associated vocabulary only — no structural analysis.

    Use this for a quick check when you just want to find and replace AI words
    without running the full analysis pipeline.

    Args:
        params (VocabCheckInput): Contains the text to scan.

    Returns:
        str: JSON with found AI words, their positions, and replacement suggestions.
    """
    text = params.text
    vocab = find_ai_vocabulary(text)
    phrases = find_ai_phrases(text)

    return json.dumps(
        {
            "ai_words_found": len(vocab),
            "ai_words": vocab,
            "ai_phrases_found": len(phrases),
            "ai_phrases": phrases,
            "quick_fix_map": {
                v["word"]: AI_VOCABULARY[v["word"]][0]
                if AI_VOCABULARY[v["word"]][0]
                else "(delete)"
                for v in vocab
            },
        },
        indent=2,
    )


@mcp.tool(
    name="humanizer_get_rewrite_instructions",
    annotations={
        "title": "Get Humanization Rewrite Instructions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_rewrite_instructions(params: HumanizeTextInput) -> str:
    """Analyze AI text and return detailed, step-by-step rewrite instructions.

    This tool does NOT rewrite the text itself — it provides a structured
    action plan that an LLM or human editor can follow to humanize the text.
    The instructions are tailored to the text type and specific patterns found.

    Args:
        params (HumanizeTextInput): Contains text, text type, and voice preferences.

    Returns:
        str: JSON with analysis results and step-by-step rewrite instructions.
    """
    text = params.text
    text_type = params.text_type

    vocab = find_ai_vocabulary(text)
    phrases = find_ai_phrases(text)
    sent_lengths = sentence_lengths(text)
    burstiness_val = calculate_burstiness(sent_lengths)
    contractions = check_contraction_usage(text)
    para_uni = check_paragraph_uniformity(text)
    rq = check_rhetorical_questions(text)
    fp = check_first_person(text)
    em = count_em_dashes(text)
    wc = count_words(text)

    analysis = {
        "word_count": wc,
        "ai_vocabulary_count": len(vocab),
        "ai_phrase_count": len(phrases),
        "burstiness": burstiness_val,
        "em_dash_count": em,
    }

    risk = compute_risk_score(
        {
            "word_count": wc,
            "ai_vocabulary_count": len(vocab),
            "ai_phrase_count": len(phrases),
            "burstiness": burstiness_val,
            "contractions": contractions,
            "paragraph_uniformity": para_uni,
            "rhetorical_questions": rq,
            "first_person": fp,
            "em_dash_count": em,
        }
    )

    instructions: list[dict[str, Any]] = []

    instructions.append(
        {
            "step": 1,
            "action": "REWRITE INTRODUCTION",
            "detail": "Delete the first 2-3 sentences entirely. Write a new opening that starts with a specific detail, bold claim, or anecdote. No preambles.",
            "priority": "critical",
        }
    )

    if vocab:
        swap_map: dict[str, str] = {}
        for v in vocab:
            w = v["word"]
            if w not in swap_map:
                replacements = AI_VOCABULARY.get(w, [])
                swap_map[w] = replacements[0] if replacements and replacements[0] else "(delete)"
        instructions.append(
            {
                "step": 2,
                "action": "REPLACE AI VOCABULARY",
                "detail": f"Find and replace these {len(swap_map)} AI-associated words",
                "swaps": swap_map,
                "priority": "critical",
            }
        )

    if phrases:
        instructions.append(
            {
                "step": 3,
                "action": "REMOVE AI PHRASES",
                "detail": "Delete or completely rephrase these cliché AI constructions",
                "phrases_to_kill": list({p["phrase"] for p in phrases}),
                "priority": "high",
            }
        )

    if burstiness_val < 0.35:
        instructions.append(
            {
                "step": 4,
                "action": "INCREASE SENTENCE LENGTH VARIATION",
                "detail": f"Current burstiness: {burstiness_val} (target: >0.45). Current lengths: {sent_lengths[:10]}... Mix in 3-5 word sentences after long ones. Add sentence fragments. Break up any run of similar-length sentences.",
                "priority": "high",
            }
        )

    if contractions.get("assessment") == "AI-like (too formal)":
        if text_type in [TextType.BLOG, TextType.EMAIL]:
            contraction_level = "heavy"
            frequency = "use them everywhere"
        elif text_type == TextType.GENERAL:
            contraction_level = "moderate"
            frequency = "use them selectively and inconsistently"
        else:
            contraction_level = "light and inconsistent"
            frequency = "use them selectively and inconsistently"
        instructions.append(
            {
                "step": 5,
                "action": "ADD CONTRACTIONS",
                "detail": f"Use {contraction_level} contractions. Change 'it is' → 'it's', 'do not' → 'don't', 'we have' → 'we've'. For {text_type.value} text, {frequency}.",
                "priority": "medium",
            }
        )

    if para_uni.get("assessment") == "too uniform (AI-like)":
        instructions.append(
            {
                "step": 6,
                "action": "CREATE PARAGRAPH ASYMMETRY",
                "detail": f"Current paragraph lengths: {para_uni.get('lengths', [])}. Mix one-sentence paragraphs with dense 6-8 sentence paragraphs. No two consecutive paragraphs should be similar length.",
                "priority": "medium",
            }
        )

    if em >= 3:
        instructions.append(
            {
                "step": 7,
                "action": "REDUCE EM DASHES",
                "detail": f"Found {em} em dashes. Replace all but 1-2 with commas, periods, or parentheses. This is a known ChatGPT signature.",
                "priority": "medium",
            }
        )

    voice_instruction = params.voice_notes or "natural, conversational"
    instructions.append(
        {
            "step": len(instructions) + 1,
            "action": "INJECT HUMAN VOICE",
            "detail": f"Target voice: {voice_instruction}. Add: (1) at least one first-person claim per major section, (2) 1-2 rhetorical questions, (3) specific proper nouns/dates/tool names, (4) at least one opinion or subjective judgment, (5) at least one admission of limitation or uncertainty.",
            "priority": "high" if "weak" in fp.get("assessment", "") else "medium",
        }
    )

    instructions.append(
        {
            "step": len(instructions) + 1,
            "action": "FINAL READ-ALOUD PASS",
            "detail": "Read the entire piece aloud (or mentally). Mark anything that sounds metronomic, robotic, or that you would never say in conversation. Fix those spots.",
            "priority": "required",
        }
    )

    return json.dumps(
        {
            "analysis_summary": analysis,
            "risk_assessment": risk,
            "text_type": text_type.value,
            "preserve_meaning": params.preserve_meaning,
            "rewrite_instructions": instructions,
            "instruction_count": len(instructions),
        },
        indent=2,
    )


@mcp.tool(
    name="humanizer_compare_before_after",
    annotations={
        "title": "Compare Before/After Detection Metrics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def compare_before_after(original: str, rewritten: str) -> str:
    """Compare detection metrics between original and rewritten text.

    Use after humanizing to verify improvement. Shows side-by-side
    metrics for burstiness, vocabulary tells, structure, and risk scores.

    Args:
        original (str): The original AI-generated text.
        rewritten (str): The humanized version.

    Returns:
        str: JSON comparison of detection metrics for both versions.
    """

    def quick_analysis(text: str) -> dict[str, Any]:
        vocab = find_ai_vocabulary(text)
        phrases = find_ai_phrases(text)
        sl = sentence_lengths(text)
        burst = calculate_burstiness(sl)
        contr = check_contraction_usage(text)
        para = check_paragraph_uniformity(text)
        rq = check_rhetorical_questions(text)
        fp = check_first_person(text)
        em = count_em_dashes(text)
        wc = count_words(text)

        risk = compute_risk_score(
            {
                "word_count": wc,
                "ai_vocabulary_count": len(vocab),
                "ai_phrase_count": len(phrases),
                "burstiness": burst,
                "contractions": contr,
                "paragraph_uniformity": para,
                "rhetorical_questions": rq,
                "first_person": fp,
                "em_dash_count": em,
            }
        )

        return {
            "word_count": wc,
            "sentence_count": len(sl),
            "ai_vocabulary_count": len(vocab),
            "ai_phrase_count": len(phrases),
            "burstiness": burst,
            "contraction_assessment": contr.get("assessment"),
            "paragraph_uniformity": para.get("assessment"),
            "rhetorical_questions": rq,
            "first_person_count": fp.get("total_occurrences", 0),
            "em_dash_count": em,
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
        }

    orig = quick_analysis(original)
    rewr = quick_analysis(rewritten)

    improvements: dict[str, str] = {}
    for key in ["ai_vocabulary_count", "ai_phrase_count", "risk_score", "em_dash_count"]:
        diff = orig.get(key, 0) - rewr.get(key, 0)
        improvements[key] = (
            f"{'improved' if diff > 0 else 'unchanged' if diff == 0 else 'worsened'} (Δ{diff:+d})"
        )

    burst_diff = rewr.get("burstiness", 0) - orig.get("burstiness", 0)
    improvements["burstiness"] = (
        f"{'improved' if burst_diff > 0 else 'unchanged' if burst_diff == 0 else 'worsened'} (Δ{burst_diff:+.3f})"
    )

    if rewr["risk_score"] <= 20:
        verdict = "PASS — likely undetectable"
    elif rewr["risk_score"] < orig["risk_score"]:
        verdict = "IMPROVED but still risky"
    else:
        verdict = "NEEDS MORE WORK"

    return json.dumps(
        {
            "original": orig,
            "rewritten": rewr,
            "improvements": improvements,
            "overall_verdict": verdict,
        },
        indent=2,
    )


@mcp.tool(
    name="humanizer_get_banned_words",
    annotations={
        "title": "Get Full AI Vocabulary Ban List",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_banned_words() -> str:
    """Return the complete list of AI-associated words and their human replacements.

    Use as a reference when manually editing text. Includes both single words
    and multi-word phrases that trigger AI detection.

    Returns:
        str: JSON with vocabulary ban list and phrase ban list.
    """
    return json.dumps(
        {
            "vocabulary_ban_list": dict(AI_VOCABULARY),
            "phrase_ban_list": AI_PHRASES,
            "vocabulary_count": len(AI_VOCABULARY),
            "phrase_count": len(AI_PHRASES),
        },
        indent=2,
    )


# ─────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────


def main() -> None:
    """CLI entry point registered in pyproject.toml as `humanizer-mcp`."""
    from humanizer_mcp import __version__

    parser = argparse.ArgumentParser(
        prog="humanizer-mcp",
        description="MCP server for analyzing and humanizing AI-generated text.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"humanizer-mcp {__version__}",
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run as streamable-HTTP server instead of stdio (default).",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Bind address for HTTP transport (default: 0.0.0.0, or $HOST).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="Port for HTTP transport (default: 8000, or $PORT).",
    )
    args = parser.parse_args()

    if args.http:
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.settings.transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        )
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
