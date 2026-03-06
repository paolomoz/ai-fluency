"""
Generate a structured evidence report for Claude Code to assess.

The report is a markdown file containing all collected evidence,
organized by the 24 behaviors of the AI fluency framework.
"""

import random
from datetime import datetime
from pathlib import Path
from typing import Optional

from ai_fluency.framework import BEHAVIORS, COMPETENCIES, SUB_COMPETENCIES

MAX_SAMPLES = 300


def _select_diverse_samples(samples: list, max_count: int = MAX_SAMPLES) -> list:
    """Select a diverse set of samples across projects, preferring longer messages."""
    if len(samples) <= max_count:
        return samples

    # Group by project
    by_project = {}
    for s in samples:
        key = s.get("project", s.get("conversation", "unknown"))
        by_project.setdefault(key, []).append(s)

    # Sort each project's messages by length (longer = richer signal), descending
    for key in by_project:
        by_project[key].sort(key=lambda s: len(s.get("text", "")), reverse=True)

    # Round-robin pick from each project, taking longest first
    selected = []
    projects = list(by_project.keys())
    random.seed(42)  # reproducible
    random.shuffle(projects)

    idx = 0
    while len(selected) < max_count:
        project = projects[idx % len(projects)]
        msgs = by_project[project]
        if msgs:
            selected.append(msgs.pop(0))
        else:
            projects.remove(project)
            if not projects:
                break
        idx += 1

    return selected


def generate_report(
    evidence: dict,
    output_path: Optional[Path] = None,
) -> str:
    """Generate the full assessment report as markdown."""
    lines = []
    lines.append("# AI Fluency Assessment Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # --- Data sources summary ---
    lines.append("## Data Sources Collected")
    lines.append("")

    claude_ai = evidence.get("claude_ai")
    if claude_ai and claude_ai.get("found"):
        lines.append(f"- **Claude.ai conversations**: {claude_ai['total_conversations']} conversations, "
                      f"{claude_ai['total_user_messages']} user messages")
    else:
        lines.append("- **Claude.ai conversations**: Not provided")

    claude_code = evidence.get("claude_code")
    if claude_code and claude_code.get("found"):
        lines.append(f"- **Claude Code sessions**: {claude_code['sessions_parsed']} sessions across "
                      f"{len(claude_code.get('projects', []))} projects, "
                      f"{claude_code['total_user_messages']} user messages")
    else:
        lines.append("- **Claude Code sessions**: Not found")

    git_data = evidence.get("git")
    if git_data:
        for repo in git_data:
            if repo.get("found"):
                lines.append(f"- **Git repo ({repo['repo']})**: {repo['total_commits']} commits, "
                              f"{repo['ai_coauthored_commits']} AI co-authored")
    else:
        lines.append("- **Git history**: Not provided")

    questionnaire = evidence.get("questionnaire")
    if questionnaire and questionnaire.get("found"):
        lines.append(f"- **Self-assessment**: {len(questionnaire['responses'])} questions answered")
    else:
        lines.append("- **Self-assessment**: Not completed")

    lines.append("")

    # --- Framework reference ---
    lines.append("## Assessment Framework")
    lines.append("")
    lines.append("Based on the 4D AI Fluency Framework (Dakan, Feller & Anthropic, 2025).")
    lines.append("4 Competencies, 12 Sub-competencies, 24 Behaviors.")
    lines.append("")
    lines.append("### Scoring Guide")
    lines.append("")
    lines.append("For each behavior, assess on a 1-5 scale:")
    lines.append("- **1 - Novice**: No evidence of this behavior")
    lines.append("- **2 - Emerging**: Occasional or inconsistent evidence")
    lines.append("- **3 - Developing**: Regular evidence but room for improvement")
    lines.append("- **4 - Proficient**: Consistent, effective demonstration")
    lines.append("- **5 - Expert**: Sophisticated, nuanced mastery")
    lines.append("")

    # --- Evidence by behavior ---
    lines.append("## Evidence by Behavior")
    lines.append("")

    for competency in COMPETENCIES:
        lines.append(f"### {competency}")
        lines.append("")
        for sub in SUB_COMPETENCIES[competency]:
            lines.append(f"#### {sub}")
            lines.append("")
            behaviors = [b for b in BEHAVIORS if b.sub_competency == sub]
            for b in behaviors:
                lines.append(f"**Behavior {b.id}: {b.name}** {'(Observable)' if b.observable else '(Self-assessed)'}")
                lines.append(f"> {b.description}")
                lines.append("")

                # Add self-assessment score if available
                if not b.observable and questionnaire and questionnaire.get("found"):
                    for resp in questionnaire["responses"]:
                        if resp["behavior_id"] == b.id:
                            lines.append(f"Self-assessment rating: **{resp['rating']}/5**")
                            lines.append("")
                            break

            lines.append("")

    # --- Raw evidence appendix ---
    lines.append("## Appendix: Raw Evidence Samples")
    lines.append("")

    # Claude.ai samples
    if claude_ai and claude_ai.get("found"):
        lines.append("### Claude.ai Conversation Samples")
        lines.append("")
        samples = _select_diverse_samples(claude_ai.get("samples", []))
        for sample in samples:
            lines.append(f"**[{sample['conversation']}]**")
            lines.append("```")
            lines.append(sample["text"][:1500])
            lines.append("```")
            lines.append("")

    # Claude Code samples
    if claude_code and claude_code.get("found"):
        lines.append("### Claude Code Session Samples")
        lines.append("")
        samples = _select_diverse_samples(claude_code.get("samples", []))
        lines.append(f"*{len(samples)} samples selected from "
                      f"{claude_code['total_user_messages']} total messages "
                      f"across {len(claude_code.get('projects', []))} projects*")
        lines.append("")
        for sample in samples:
            lines.append(f"**[Project: {sample['project']}]**")
            lines.append("```")
            lines.append(sample["text"][:1500])
            lines.append("```")
            lines.append("")

    # Git evidence
    if git_data:
        lines.append("### Git History")
        lines.append("")
        for repo in git_data:
            if not repo.get("found"):
                continue
            lines.append(f"**Repo: {repo['repo']}**")
            lines.append("")
            if repo["ai_coauthored_commits"] > 0:
                lines.append(f"AI co-authored commits ({repo['ai_coauthored_commits']}):")
                for c in repo["ai_commits"][:20]:
                    lines.append(f"- `{c['hash']}` {c['subject']} ({c['date'][:10]})")
                lines.append("")
            lines.append("Recent commits:")
            for c in repo["recent_commits"]:
                lines.append(f"- `{c['hash']}` {c['subject']} ({c['date'][:10]})")
            lines.append("")

    # --- Assessment prompt ---
    lines.append("## Assessment Instructions for Claude")
    lines.append("")
    lines.append("Analyze the evidence above and produce an AI Fluency Assessment:")
    lines.append("")
    lines.append("1. **Score each of the 24 behaviors** (1-5) based on the evidence samples "
                  "and self-assessment ratings. For observable behaviors, base scores primarily "
                  "on the conversation/session evidence. For unobservable behaviors, use the "
                  "self-assessment ratings as a starting point but adjust based on any "
                  "corroborating evidence.")
    lines.append("")
    lines.append("2. **Compute sub-competency scores** (average of behavior scores within each).")
    lines.append("")
    lines.append("3. **Compute competency scores** (average of sub-competency scores).")
    lines.append("")
    lines.append("4. **Compute overall AI Fluency score** (average of competency scores).")
    lines.append("")
    lines.append("5. **Provide a narrative assessment** for each competency highlighting:")
    lines.append("   - Strongest demonstrated behaviors with specific evidence")
    lines.append("   - Areas for improvement with concrete recommendations")
    lines.append("   - Patterns observed across interactions")
    lines.append("")
    lines.append("6. **Provide an overall summary** including:")
    lines.append("   - Overall fluency level (Novice/Emerging/Developing/Proficient/Expert)")
    lines.append("   - Top 3 strengths")
    lines.append("   - Top 3 areas for growth")
    lines.append("   - Specific, actionable next steps")
    lines.append("")
    lines.append("Present the scores in a table format and keep the narrative concise but evidence-based.")

    report = "\n".join(lines)

    if output_path:
        output_path.write_text(report)

    return report
