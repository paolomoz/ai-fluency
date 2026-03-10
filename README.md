# AI Fluency Assessment

Scan your AI activity and get a detailed assessment of your AI fluency based on **Anthropic's 4D Framework** (Dakan, Feller & Anthropic, 2025). Graded on a **CEFR-aligned scale** (A1→C2) — the same system used for human language certification worldwide.

Runs locally via Claude Code — no API calls, no data leaves your machine.

![AI Fluency Report — Overall score, heuristic analysis, and competency breakdown](docs/hero.png?v=2)

## What it measures

The 4D Framework defines **24 behaviors** across 4 competencies:

| Competency | What it covers | Behaviors |
|-----------|---------------|-----------|
| **Delegation** | Knowing when and how to use AI | 1–6 |
| **Description** | Communicating effectively with AI | 7–12 |
| **Discernment** | Evaluating AI outputs critically | 13–18 |
| **Diligence** | Using AI responsibly and ethically | 19–24 |

**11 behaviors** are observable from your conversation data. **13 behaviors** are assessed via self-report questionnaire.

## How it works

```
┌─────────────────────────────────────────────────────┐
│  1. COLLECT                                         │
│     Claude Code sessions  ·  Claude.ai exports      │
│     Git history (AI co-authored commits)             │
├─────────────────────────────────────────────────────┤
│  2. ANALYZE                                         │
│     Regex heuristics scan every message for          │
│     11 observable behavior patterns                  │
├─────────────────────────────────────────────────────┤
│  3. QUESTIONNAIRE                                   │
│     13 self-assessment questions for                 │
│     unobservable behaviors (1-5 scale)               │
├─────────────────────────────────────────────────────┤
│  4. SCORE & REPORT                                  │
│     24 behavior scores → 12 sub-competencies →       │
│     4 competencies → overall fluency score           │
│     Visual HTML report with actionable feedback      │
└─────────────────────────────────────────────────────┘
```

## The report

### Full-coverage heuristic analysis

Every message is scanned against behavior patterns. Bars are scaled relative to the strongest behavior — no misleading percentages.

![Heuristic heatmap and project breakdown](docs/heatmap.png?v=2)

### Per-behavior cards with evidence and actions

Each of the 24 behaviors gets a dedicated card with score, evidence from your actual conversations, and concrete next steps.

![Behavior cards with evidence and actionable recommendations](docs/behavior-card.png?v=2)

## Usage

### Quick start (via Claude Code skill)

If you have the `ai-fluency-assessment` skill installed:

```
> assess my AI fluency
```

Claude Code will walk you through collection, questionnaire, and report generation.

### Manual

```bash
# Install
cd ai-fluency
export PYTHONPATH=$PWD/src

# 1. Collect evidence (scans ~/.claude/projects/ automatically)
python3 -m ai_fluency collect --max-sessions 2000

# 2. Run heuristic analysis
python3 -c "
from pathlib import Path
from ai_fluency.heuristics import analyze_all_messages, print_summary
import json

results = analyze_all_messages(Path('.ai-fluency/evidence.json'))
print_summary(results)
with open('.ai-fluency/heuristic-analysis.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
"

# 3. Run questionnaire (interactive)
python3 -m ai_fluency questionnaire

# 4. Generate markdown report
python3 -m ai_fluency report

# 5. Open the visual HTML report
open .ai-fluency/fluency-report.html
```

### Options

```bash
# Include Claude.ai conversation export
python3 -m ai_fluency collect --claude-export ~/Downloads/claude-export/

# Scan git repos for AI co-authored commits
python3 -m ai_fluency collect --scan-dirs ~/projects ~/work

# Focus on your top 10 projects only
python3 -m ai_fluency collect --max-sessions 2000 --top-projects 10
```

## The 24 behaviors

| # | Behavior | Type |
|---|----------|------|
| 1 | Clarifies goal before asking for help | Observable |
| 2 | Understands problem scope and nature | Self-assessed |
| 3 | Assesses AI fit | Self-assessed |
| 4 | Selects platform | Self-assessed |
| 5 | Consults AI on approach before execution | Observable |
| 6 | Distributes work strategically | Self-assessed |
| 7 | Specifies format and structure needed | Observable |
| 8 | Defines audience for the output | Observable |
| 9 | Provides examples of what good looks like | Observable |
| 10 | Iterates and refines | Observable |
| 11 | Sets interaction mode | Observable |
| 12 | Communicates tone and style preferences | Observable |
| 13 | Checks facts and claims that matter | Observable |
| 14 | Identifies when AI might be missing context | Observable |
| 15 | Questions when AI reasoning doesn't hold up | Observable |
| 16 | Detects hallucination | Self-assessed |
| 17 | Evaluates tone and communication fit | Self-assessed |
| 18 | Recognizes bias in AI outputs | Self-assessed |
| 19 | Chooses AI tools ethically | Self-assessed |
| 20 | Maintains ethical awareness during interaction | Self-assessed |
| 21 | Discloses AI involvement to stakeholders | Self-assessed |
| 22 | Represents AI contribution accurately | Self-assessed |
| 23 | Verifies and tests outputs before sharing | Self-assessed |
| 24 | Takes ongoing accountability | Self-assessed |

## Requirements

- Python 3.10+
- Claude Code sessions in `~/.claude/projects/` (automatic if you use Claude Code)
- No external dependencies

## References

- [AI Fluency Isn't Prompting — Anthropic's New Research Proves It](https://www.linkedin.com/pulse/ai-fluency-isnt-prompting-anthropics-new-research-proves-cathey-ccqje/) — Glen Cathey
- [AI Fluency Framework](https://www.anthropic.com/research/ai-fluency) — Dakan, Feller & Anthropic, 2025

## License

MIT
