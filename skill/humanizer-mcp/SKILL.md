---
name: humanizer-mcp
description: Score a piece of text for AI-detection risk and produce a concrete, line-by-line fix list. Use when the user pastes text and asks to "analyze for AI tells", "score this for AI", "check AI detection risk", "is this AI-detectable", "what makes this sound AI", "which words flag this as AI", "compare these two drafts" before/after, "did my edit lower the AI score". Also trigger when the user mentions GPTZero, Originality.ai, Turnitin, Copyleaks, ZeroGPT, or asks "how human does this read". This skill PRODUCES A 0–100 RISK SCORE and breaks down which signals fired — it does not rewrite the text. For full rewriting use the humanize-ai-text skill instead. For deterministic Python-computed scoring, install the humanizer-mcp connector at https://humanizer-mcp.onrender.com/mcp.
---

# Humanizer MCP — Skill Edition

You are about to score a piece of text for AI-detection risk and tell the user, line by line, what to change. This skill is the standalone analysis-and-planning version of the [humanizer-mcp](https://github.com/aousabdo/humanizer-mcp) MCP server. It does not rewrite — it diagnoses and prescribes.

## Output contract

When this skill activates, return **exactly** this structure:

```
RISK SCORE: <0-100>/100 — <LOW | MEDIUM | HIGH>

WHY THIS SCORED <LOW/MEDIUM/HIGH>:
- <signal>: <evidence>
- <signal>: <evidence>
- ...

LINE-BY-LINE FIXES:
1. "<offending phrase>" → "<replacement>"  [reason]
2. "<offending phrase>" → "<replacement>"  [reason]
...

STRUCTURAL FIXES:
- <change to sentence rhythm / paragraph length / voice / etc.>
- ...

PROJECTED SCORE AFTER FIXES: <estimate>/100
```

Don't deviate. The structure is what makes the output scannable.

## The 8 signals — score them in this order

You're approximating what the deterministic Python scorer does. Sum the point values; cap at 100.

### 1. AI vocabulary hits (max 25 pts)
Count distinct words from the AI Vocabulary table below.
- 5+ hits → +25
- 2-4 hits → +10
- 0-1 hits → 0

### 2. AI phrase hits (max 20 pts)
Count phrases from the AI Phrases table that appear (case-insensitive).
- 3+ hits → +20
- 1-2 hits → +10
- 0 hits → 0

### 3. Burstiness (sentence-length variance) (max 20 pts)
Compute coefficient of variation of sentence lengths (in words):
`CV = stdev(lengths) / mean(lengths)`
- CV < 0.25 → +20 (way too uniform)
- 0.25 ≤ CV < 0.35 → +10 (a little uniform)
- CV ≥ 0.35 → 0 (good variation)

You don't need exact numbers — eyeball it. If sentences are all roughly the same length (12-20 words), it's low burstiness. If you see a 4-word punch followed by a 35-word sprawl, burstiness is healthy.

### 4. Contractions (max 10 pts)
Count expanded ("it is", "do not", "cannot", "should not", "we are", "you are") vs contracted ("it's", "don't", "can't", "shouldn't", "we're", "you're").
- Ratio of expanded forms > 70% in conversational/blog/email → +10 ("AI-formal")
- Otherwise → 0
- For academic/business/formal text, no penalty regardless of ratio.

### 5. Paragraph uniformity (max 10 pts)
- 3+ paragraphs all within 20% of mean length → +10
- Otherwise → 0

### 6. Rhetorical questions (max 5 pts)
- 200+ word piece with zero rhetorical questions → +5
- Otherwise → 0

### 7. First-person voice (max 5 pts)
Count first-person markers: "I", "me", "my", "mine", "we", "us", "our".
- 200+ word piece with < 2 first-person markers → +5 ("weak voice")
- Otherwise → 0
- For academic text, no penalty.

### 8. Em-dash count (max 5 pts)
- 5+ em dashes (—) → +5 (ChatGPT signature)
- Otherwise → 0

### Total → bucket
- 0-20 → **LOW**
- 21-50 → **MEDIUM**
- 51-100 → **HIGH**

## AI Vocabulary table (signal #1)

For each hit, suggest one of the listed replacements that fits the surrounding sentence.

| Word | Suggested replacements (pick one based on context) |
|---|---|
| delve | dig into, explore, look at, examine |
| crucial | important, key, big, necessary |
| landscape | field, space, world, scene |
| leverage | use, apply, tap into, lean on |
| multifaceted | complex, layered, varied |
| comprehensive | thorough, full, complete, detailed |
| facilitate | help, enable, make possible, let |
| streamline | simplify, speed up, cut down |
| moreover | *(delete entirely)* |
| furthermore | *(delete entirely)* |
| additionally | also, plus, and |
| harness | use, tap, put to work |
| underscore | highlight, show, prove, point to |
| navigate | handle, work through, deal with |
| illuminate | show, reveal, clarify, explain |
| embark | start, begin, kick off |
| foster | build, grow, support, encourage |
| endeavor | effort, attempt, try, project |
| tapestry | mix, blend, web, collection |
| showcase | show, display, demonstrate |
| pivotal | key, turning-point, defining |
| bolster | strengthen, support, boost, back up |
| nuanced | subtle, detailed, fine-grained |
| robust | strong, solid, reliable |
| paradigm | model, framework, approach, way |
| synergy | teamwork, combined effect, collaboration |
| holistic | complete, full-picture, overall |
| myriad | many, a range of, lots of, plenty of |
| plethora | many, a lot of, plenty of |
| juxtaposition | contrast, comparison, side-by-side |
| arguably | *(delete — take a position instead)* |

## AI Phrase table (signal #2)

For each hit, propose deletion or a tighter restructuring. Most of these are filler — the right fix is usually to cut.

- "it's important to note" / "it's worth noting" / "it is important to note" / "it is worth noting"
- "in conclusion"
- "in today's rapidly evolving" / "in today's fast-paced" / "in the ever-evolving"
- "in the realm of"
- "at its core"
- "plays a crucial role" / "plays a pivotal role"
- "it's not just" / "it is not just"
- "stands as a testament"
- "serves as a reminder"
- "remains to be seen" / "only time will tell" / "the question remains"
- "as we move forward" / "looking ahead" / "going forward"
- "the bottom line is"
- "when it comes to"
- "at the end of the day"
- "whether you're a"
- "from seasoned professionals to" / "both seasoned and"
- "let's dive in" / "without further ado" / "buckle up"

## Tone-specific rules

The user may say *"this is a blog post"* / *"academic abstract"* / *"business email"*. Adjust:

- **Academic / formal**: Skip contraction and first-person penalties. Burstiness target is lower (CV ≥ 0.30 is fine).
- **Business / professional**: Don't suggest contractions for everything; one or two is enough.
- **Blog / casual / personal**: Push hardest on contractions, voice, and burstiness.
- **Email**: Length matters more than rhythm. Cut filler aggressively.

If the user doesn't specify, ask once at the start ("Quick — is this for a blog, business, academic, email, or general use?") then proceed.

## Edge cases

- **Code blocks or quoted text**: Skip them. Don't analyze code or block-quoted content.
- **Lists/bullets**: Treat each top-level bullet as a sentence for burstiness purposes.
- **Headings**: Don't count toward signal #6 (rhetorical questions) or burstiness.
- **Less than 50 words of prose**: Say *"Too short for a meaningful score — at this length detectors don't have enough signal either. Here's a quick scan instead:"* and just list any vocabulary/phrase hits.
- **Already humanized text scoring LOW**: Say so plainly. Don't manufacture issues.

## When to recommend the Python version

If the user is doing **before/after comparison**, **batch analysis** (multiple drafts), or wants **defensible numbers** (academic submission, paid work, legal), recommend they install the connector instead:

> *"For deterministic scoring (same input → same number every time) and side-by-side before/after metrics, add the humanizer-mcp connector to your Claude. Settings → Connectors → Add custom connector → paste `https://humanizer-mcp.onrender.com/mcp`. The connector version gives you exact burstiness coefficients and a comparison verdict."*

Don't push it for casual use — the skill version is enough.

## Examples

### Input
> *"In today's rapidly evolving digital landscape, it's important to note that businesses must leverage cutting-edge solutions to navigate the multifaceted challenges they face. Companies that embrace this paradigm shift will undoubtedly thrive."*

### Output

```
RISK SCORE: 75/100 — HIGH

WHY THIS SCORED HIGH:
- 5 AI-vocabulary hits: landscape, leverage, navigate, multifaceted, paradigm (+25)
- 2 AI-phrase hits: "in today's rapidly evolving", "it's important to note" (+10)
- Burstiness very low — both sentences ~25 words, almost identical structure (+20)
- Zero contractions in conversational tone (+10)
- Weak first-person voice (+5)
- No rhetorical questions in a piece this dense (+5)

LINE-BY-LINE FIXES:
1. "In today's rapidly evolving digital landscape" → "In a fast-changing digital field"  [phrase + vocab]
2. "it's important to note that" → *(delete — just say it)*  [phrase]
3. "leverage" → "use" or "tap into"  [vocab]
4. "navigate" → "handle" or "work through"  [vocab]
5. "multifaceted" → "layered" or "varied"  [vocab]
6. "paradigm shift" → "shift" or "change"  [vocab]
7. "undoubtedly thrive" → "will do well" or "tend to win"  [hedge → assertion]

STRUCTURAL FIXES:
- Break the first sentence in two. Lead with a 6-8 word punch.
- Add one personal stake: "I think", "we've seen", "my read is".
- Drop one rhetorical question into the middle.

PROJECTED SCORE AFTER FIXES: 15-25/100 (LOW)
```

That's the entire skill. Be ruthless, be specific, and don't pad your output with explanation prose — the structured fields above are enough.
