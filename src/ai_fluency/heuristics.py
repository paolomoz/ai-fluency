"""
Heuristic analysis of all messages for observable behavior signals.

Scans every message for patterns that indicate each of the 11 observable behaviors.
Returns frequency counts, consistency metrics, and per-project breakdowns.
"""

import re
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict
from typing import Optional


# Pattern definitions for each observable behavior.
# Each behavior has multiple signal patterns — a message matching ANY pattern counts.
# Patterns are tuned to minimize false positives.

BEHAVIOR_PATTERNS = {
    1: {
        "name": "Clarifies goal before asking for help",
        "patterns": [
            # Explicit plan/goal statements
            r"(?i)implement the following plan",
            r"(?i)^#\s+plan:",
            r"(?i)##\s+context\b",
            r"(?i)##\s+goal",
            r"(?i)##\s+objective",
            r"(?i)##\s+approach",
            r"(?i)##\s+architecture",
            r"(?i)##\s+what it does",
            r"(?i)##\s+requirements",
            r"(?i)i want to\s+(build|create|make|implement|add|design|set up)",
            r"(?i)i need (a|an|to)\s+\w+.*(that|which|for|to)\b",
            r"(?i)the goal is\b",
            r"(?i)we need to\b",
            r"(?i)the plan is\b",
            r"(?i)here'?s what (i|we) need",
        ],
    },
    5: {
        "name": "Consults AI on approach before execution",
        "patterns": [
            r"(?i)what do you (think|suggest|recommend)",
            r"(?i)what'?s the best (way|approach|strategy)",
            r"(?i)how (should|would|can) (we|i|you)",
            r"(?i)can you (help me|suggest|recommend|advise)",
            r"(?i)what approach",
            r"(?i)before (we|i) (start|begin|implement|build|code)",
            r"(?i)let'?s (think|plan|discuss|figure out|brainstorm)",
            r"(?i)should (we|i)\s+\w+\s+or\s+",
            r"(?i)what are (the|my|our) options",
            r"(?i)do you (think|see|notice)",
        ],
    },
    7: {
        "name": "Specifies format and structure needed",
        "patterns": [
            # File structure specs
            r"(?i)##\s+files? to (create|modify|change|update)",
            r"(?i)\|\s*file\s*\|",
            r"(?i)```(sql|js|ts|css|html|json|bash|python|yaml|toml)",
            # Explicit format instructions
            r"(?i)(format|structure|layout|schema|table|columns?):",
            r"(?i)(create|add|build|make)\s+(a|an|the)\s+\w+\s+(file|page|component|endpoint|table|migration)",
            r"(?i)(new file|modify)\s*[:`]",
            r"(?i)directory structure",
            r"(?i)CREATE TABLE",
            r"(?i)API (endpoint|route|format)",
            # Design specs
            r"(?i)#[0-9a-fA-F]{6}\b",
            r"(?i)\d+px\b",
            r"(?i)(font-size|border-radius|padding|margin|gap):",
            r"(?i)(width|height):\s*\d+",
        ],
    },
    8: {
        "name": "Defines audience for the output",
        "patterns": [
            r"(?i)(target|intended) audience",
            r"(?i)(for|aimed at|targeting)\s+(users?|customers?|developers?|stakeholders?|clients?|visitors?|readers?)",
            r"(?i)(audience|persona|demographic|user profile)\s*(is|are|:)",
            r"(?i)aged?\s+\d+[-\s]?\d*",
            r"(?i)(beginners?|experts?|non-technical|technical users?)",
            r"(?i)who (will|is going to) (use|read|see|view)",
            r"(?i)demo for\s+\w+",
            r"(?i)presentation (for|to)\s+\w+",
            r"(?i)the (viewer|reader|user|visitor) (should|will|can)",
        ],
    },
    9: {
        "name": "Provides examples of what good looks like",
        "patterns": [
            r"(?i)(here'?s|this is) (an example|a reference|what .* looks? like)",
            r"(?i)(use|follow|copy|replicate|match)\s+(the|this|that)\s+(same|existing|pattern|style|format|approach)",
            r"(?i)like (we|i) did (for|in|with|on)\s+",
            r"(?i)(same|similar) (pattern|approach|style|format|structure) (as|from|in)\s+",
            r"(?i)copied from\b",
            r"(?i)use .* as (a |an )?(reference|template|example|starting point|basis)",
            r"(?i)for example[,:]",
            r"(?i)e\.g\.\s+",
            r"(?i)here'?s what .* looks? like",
            r"(?i)use (it|these|this) to\s+(critique|compare|evaluate|improve)",
        ],
    },
    10: {
        "name": "Iterates and refines",
        "patterns": [
            r"(?i)(try|let'?s try)\s+(again|a different|another|instead)",
            r"(?i)(that'?s not|this isn'?t|not quite|almost|close but)",
            r"(?i)(fix|adjust|tweak|change|modify|update|refine|improve)\s+(the|this|that|it)",
            r"(?i)(instead|rather),?\s+(of|let'?s|try|use|make)",
            r"(?i)can you (also|additionally|change|modify|adjust|update|fix)",
            r"(?i)actually,?\s+(let'?s|i want|change|make|use)",
            r"(?i)now (let'?s|change|add|fix|update|make|do)",
            r"(?i)this session is being continued",
            r"(?i)(troubleshoot|debug|investigate)\s+(what'?s|why|the)",
            r"(?i)it('?s| is) (not working|broken|failing|still)",
        ],
    },
    11: {
        "name": "Sets interaction mode",
        "patterns": [
            r"(?i)(think|act) (like|as) (a|an)\s+\w+",
            r"(?i)don'?t (ask|stop|wait|prompt|check|confirm)",
            r"(?i)never (stop|ask|wait|prompt)",
            r"(?i)always (validate|check|test|verify|continue)",
            r"(?i)keep (going|running|building|working)",
            r"(?i)(be|stay|keep it) (concise|brief|short|detailed|thorough|verbose)",
            r"(?i)challenge (my|the|this|our)",
            r"(?i)push back (on|if|when)",
            r"(?i)(brainstorm|explore|ideate|let'?s think)",
            r"(?i)just (do it|execute|implement|build|ship|go)",
        ],
    },
    12: {
        "name": "Communicates tone and style preferences",
        "patterns": [
            r"(?i)(tone|style|voice|persona)\s+(should|:|\bis\b|must)",
            r"(?i)(energetic|premium|casual|formal|professional|playful|friendly|warm|authoritative)",
            r"(?i)(speak|write|respond|communicate)\s+(as|like|in)\b",
            r"(?i)(design director|senior engineer|expert|consultant)",
            r"(?i)(brutalist|minimal|maximalist|editorial|luxury|refined)",
            r"(?i)podcast[- ]style",
            r"(?i)(two-host|casual .* tone|conversational)",
        ],
    },
    13: {
        "name": "Checks facts and claims that matter",
        "patterns": [
            r"(?i)(check|verify|confirm|validate|test)\s+(the|this|that|if|whether|accuracy)",
            r"(?i)(is (this|that|it) (correct|accurate|right|true))",
            r"(?i)(make sure|ensure)\s+(to check|it'?s accurate|the facts?)",
            r"(?i)generated by ai.*check\b",
            r"(?i)fact[- ]check",
            r"(?i)(are you sure|how confident|is this accurate)",
            r"(?i)(test this|troubleshoot|why (is|does|doesn'?t)|what'?s (wrong|failing|broken))",
        ],
    },
    14: {
        "name": "Identifies when AI might be missing context",
        "patterns": [
            r"(?i)(you (may|might|don'?t|probably) (not )?(know|be aware|have|understand))",
            r"(?i)(here'?s (some|the|more|additional) context)",
            r"(?i)(for context|context:)",
            r"(?i)(note that|keep in mind|important(ly)?:)",
            r"(?i)(the (thing|issue|problem) (is|here)|what you'?re missing)",
            r"(?i)(actually|in fact),?\s+(the|this|it)\b",
            r"(?i)let me (explain|clarify|give you|share|provide)",
            r"(?i)(you'?re|that'?s) (wrong|incorrect|not right|off|mistaken)",
        ],
    },
    15: {
        "name": "Questions when AI reasoning doesn't hold up",
        "patterns": [
            r"(?i)(why did you|why would you|why are you)",
            r"(?i)(that doesn'?t|this doesn'?t|it doesn'?t)\s+(make sense|seem right|work|look right)",
            r"(?i)(are you sure|i don'?t think|i disagree|that'?s not)",
            r"(?i)(but|however|wait)[,.]?\s+(that|this|the|why|how|what)",
            r"(?i)(shouldn'?t (it|we|you|this)|wouldn'?t (it|that) be)",
            r"(?i)(explain|walk me through) (why|your|the) (reasoning|logic|approach|thinking)",
            r"(?i)(what about|have you considered|did you account for)",
        ],
    },
}


def analyze_message(text: str) -> dict:
    """Check a single message against all behavior patterns. Returns matched behavior IDs."""
    matches = {}
    for bid, config in BEHAVIOR_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text):
                matches[bid] = True
                break
    return matches


def analyze_all_messages(evidence_path: Path) -> dict:
    """Run heuristic analysis across ALL messages."""
    with open(evidence_path) as f:
        evidence = json.load(f)

    results = {
        "total_messages": 0,
        "behaviors": {},
        "per_project": defaultdict(lambda: {"total": 0, "behaviors": defaultdict(int)}),
        "co_occurrence": defaultdict(int),
    }

    # Initialize behavior results
    for bid, config in BEHAVIOR_PATTERNS.items():
        results["behaviors"][bid] = {
            "name": config["name"],
            "total_matches": 0,
            "match_rate": 0.0,
            "example_messages": [],
        }

    all_samples = []

    # Collect messages from all sources
    claude_code = evidence.get("claude_code", {})
    if claude_code.get("found"):
        all_samples.extend(claude_code.get("samples", []))

    claude_ai = evidence.get("claude_ai", {})
    if claude_ai.get("found"):
        all_samples.extend(claude_ai.get("samples", []))

    results["total_messages"] = len(all_samples)

    # Analyze every message
    for msg in all_samples:
        text = msg.get("text", "")
        timestamp = msg.get("timestamp")
        project = msg.get("project", msg.get("conversation", "unknown"))

        matches = analyze_message(text)
        results["per_project"][project]["total"] += 1

        for bid in matches:
            results["behaviors"][bid]["total_matches"] += 1
            results["per_project"][project]["behaviors"][bid] += 1

            # Keep up to 5 examples per behavior (prefer shorter, clearer examples)
            examples = results["behaviors"][bid]["example_messages"]
            if len(examples) < 5 and 20 < len(text) < 500:
                examples.append({"project": project, "text": text[:300]})

        # Track co-occurrences
        matched_ids = sorted(matches.keys())
        for i, a in enumerate(matched_ids):
            for b in matched_ids[i + 1:]:
                results["co_occurrence"][f"{a}+{b}"] += 1

    # Compute rates
    total = results["total_messages"]
    for bid in results["behaviors"]:
        count = results["behaviors"][bid]["total_matches"]
        results["behaviors"][bid]["match_rate"] = round(count / total * 100, 1) if total > 0 else 0

    # Convert defaultdicts for JSON serialization
    results["per_project"] = {
        k: {"total": v["total"], "behaviors": dict(v["behaviors"])}
        for k, v in results["per_project"].items()
    }
    results["co_occurrence"] = dict(results["co_occurrence"])

    return results


def print_summary(results: dict) -> None:
    """Print a human-readable summary of heuristic analysis."""
    total = results["total_messages"]
    print(f"\nHeuristic Analysis: {total} messages analyzed")
    print("=" * 65)

    for bid, data in sorted(results["behaviors"].items()):
        count = data["total_matches"]
        rate = data["match_rate"]
        bar = "#" * int(rate / 2)
        print(f"\n  B{bid:2d}. {data['name']}")
        print(f"       {count:,}/{total:,} messages ({rate}%) {bar}")

    # Top co-occurrences
    print(f"\n{'=' * 65}")
    print("Top behavior co-occurrences (appear in same message):")
    sorted_co = sorted(results["co_occurrence"].items(), key=lambda x: -x[1])[:10]
    for pair, count in sorted_co:
        a, b = pair.split("+")
        name_a = results["behaviors"][int(a)]["name"][:30]
        name_b = results["behaviors"][int(b)]["name"][:30]
        print(f"  {name_a} + {name_b}: {count}")


def _parse_timestamp(ts: str) -> Optional[datetime]:
    """Parse an ISO-format timestamp string, returning None on failure."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _window_label(start: datetime, end: datetime) -> str:
    """Build a human-readable label like 'Dec 2025 - Jan 2026'."""
    return f"{start.strftime('%b %Y')} - {end.strftime('%b %Y')}"


def analyze_trends(evidence_path: Path, window_months: int = 2) -> dict:
    """Split messages into time windows and compute per-behavior match-rate trends."""
    with open(evidence_path) as f:
        evidence = json.load(f)

    # Collect all samples (same logic as analyze_all_messages)
    all_samples = []
    claude_code = evidence.get("claude_code", {})
    if claude_code.get("found"):
        all_samples.extend(claude_code.get("samples", []))
    claude_ai = evidence.get("claude_ai", {})
    if claude_ai.get("found"):
        all_samples.extend(claude_ai.get("samples", []))

    # Parse timestamps and find global date range
    dated_messages: list[tuple[datetime, dict]] = []
    undated_messages: list[dict] = []

    for msg in all_samples:
        dt = _parse_timestamp(msg.get("timestamp"))
        if dt is not None:
            dated_messages.append((dt, msg))
        else:
            undated_messages.append(msg)

    if not dated_messages:
        return {"windows": [], "trends": {}}

    dated_messages.sort(key=lambda x: x[0])

    earliest = dated_messages[0][0]
    latest = dated_messages[-1][0]

    # Build window boundaries
    windows: list[dict] = []
    cursor_year = earliest.year
    cursor_month = earliest.month

    while True:
        start = datetime(cursor_year, cursor_month, 1, tzinfo=timezone.utc)
        end_month = cursor_month + window_months - 1
        end_year = cursor_year
        while end_month > 12:
            end_month -= 12
            end_year += 1
        # Last day of the end month
        if end_month == 12:
            end = datetime(end_year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(end_year, end_month + 1, 1, tzinfo=timezone.utc)

        # end is exclusive; compute inclusive last day string
        end_inclusive = end - timedelta(days=1)

        windows.append({
            "label": _window_label(start, end_inclusive),
            "start": start.strftime("%Y-%m-%d"),
            "end": end_inclusive.strftime("%Y-%m-%d"),
            "start_dt": start,
            "end_dt": end,
            "total_messages": 0,
            "behaviors": {bid: {"matches": 0, "rate": 0.0} for bid in BEHAVIOR_PATTERNS},
        })

        if end >= latest.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1):
            break

        cursor_month += window_months
        while cursor_month > 12:
            cursor_month -= 12
            cursor_year += 1

    # Assign dated messages to windows
    for dt, msg in dated_messages:
        text = msg.get("text", "")
        matches = analyze_message(text)
        for win in windows:
            if win["start_dt"] <= dt < win["end_dt"]:
                win["total_messages"] += 1
                for bid in matches:
                    win["behaviors"][bid]["matches"] += 1
                break

    # Compute rates and strip internal datetime keys
    for win in windows:
        total = win["total_messages"]
        for bid in win["behaviors"]:
            m = win["behaviors"][bid]["matches"]
            win["behaviors"][bid]["rate"] = round(m / total * 100, 1) if total > 0 else 0.0
        del win["start_dt"]
        del win["end_dt"]

    # Compute trends (last window vs first window)
    trends: dict = {}
    first_win = windows[0]
    last_win = windows[-1]
    for bid in BEHAVIOR_PATTERNS:
        first_rate = first_win["behaviors"][bid]["rate"]
        last_rate = last_win["behaviors"][bid]["rate"]
        change = round(last_rate - first_rate, 1)
        if change > 1.0:
            direction = "improving"
        elif change < -1.0:
            direction = "declining"
        else:
            direction = "stable"
        trends[bid] = {"direction": direction, "change": change}

    return {"windows": windows, "trends": trends}


def print_trends(trend_results: dict) -> None:
    """Print a human-readable summary of trend analysis."""
    windows = trend_results.get("windows", [])
    trends = trend_results.get("trends", {})

    if not windows:
        print("\nNo time-window data available for trend analysis.")
        return

    print(f"\nTrend Analysis: {len(windows)} time windows")
    print("=" * 65)

    for win in windows:
        print(f"\n  {win['label']}  ({win['total_messages']:,} messages)")
        for bid in sorted(win["behaviors"], key=lambda b: int(b)):
            b = win["behaviors"][bid]
            if b["matches"] > 0:
                print(f"    B{int(bid):2d}: {b['matches']:>5,} matches  ({b['rate']}%)")

    print(f"\n{'=' * 65}")
    print("Overall trends (first window -> last window):\n")
    for bid in sorted(trends, key=lambda b: int(b)):
        t = trends[bid]
        arrow = "+" if t["change"] >= 0 else ""
        name = BEHAVIOR_PATTERNS[int(bid)]["name"]
        print(f"  B{int(bid):2d}. {name:<45s}  {t['direction']:<10s} ({arrow}{t['change']}%)")


if __name__ == "__main__":
    evidence = Path(".ai-fluency/evidence.json")

    results = analyze_all_messages(evidence)
    print_summary(results)

    # Save full results
    out = Path(".ai-fluency/heuristic-analysis.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {out}")

    # Trend analysis
    trend_results = analyze_trends(evidence)
    print_trends(trend_results)

    trend_out = Path(".ai-fluency/trend-analysis.json")
    with open(trend_out, "w") as f:
        json.dump(trend_results, f, indent=2, default=str)
    print(f"\nTrend results saved to {trend_out}")
