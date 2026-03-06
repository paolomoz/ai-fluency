"""
AI Fluency Assessment Tool

Collects evidence from your AI activity and generates a structured report
for Claude Code to assess your AI fluency against Anthropic's 4D framework.

Usage:
    python -m ai_fluency collect [options]
    python -m ai_fluency questionnaire
    python -m ai_fluency report
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from ai_fluency.collectors.claude_conversations import analyze_conversations
from ai_fluency.collectors.claude_code_sessions import analyze_sessions
from ai_fluency.collectors.git_history import scan_repos
from ai_fluency.collectors.questionnaire import (
    run_questionnaire,
    format_questionnaire_results,
)
from ai_fluency.report import generate_report


DEFAULT_OUTPUT_DIR = Path.cwd() / ".ai-fluency"
EVIDENCE_FILE = "evidence.json"
REPORT_FILE = "assessment-report.md"


def cmd_collect(args: argparse.Namespace) -> None:
    """Collect evidence from all available sources."""
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    evidence = {}

    # Load existing evidence if any
    evidence_path = output_dir / EVIDENCE_FILE
    if evidence_path.exists():
        with open(evidence_path) as f:
            evidence = json.load(f)

    # Claude.ai conversations
    if args.claude_export:
        print(f"Scanning Claude.ai export: {args.claude_export}")
        evidence["claude_ai"] = analyze_conversations(Path(args.claude_export))
        if evidence["claude_ai"].get("found"):
            print(f"  Found {evidence['claude_ai']['total_conversations']} conversations, "
                  f"{evidence['claude_ai']['total_user_messages']} messages")
        else:
            print(f"  {evidence['claude_ai'].get('error', 'No data found')}")

    # Claude Code sessions
    if not args.skip_claude_code:
        claude_code_dir = Path(args.claude_code_dir) if args.claude_code_dir else None
        print("Scanning Claude Code sessions...")
        evidence["claude_code"] = analyze_sessions(claude_code_dir, max_sessions=args.max_sessions)
        if evidence["claude_code"].get("found"):
            print(f"  Found {evidence['claude_code']['sessions_parsed']} sessions, "
                  f"{evidence['claude_code']['total_user_messages']} messages across "
                  f"{len(evidence['claude_code'].get('projects', []))} projects")
        else:
            print(f"  {evidence['claude_code'].get('error', 'No data found')}")

    # Git repos — from explicit paths and/or directory scanning
    repo_paths = []
    if args.repos:
        repo_paths.extend(Path(r) for r in args.repos)
    if args.scan_dirs:
        for scan_dir in args.scan_dirs:
            scan_path = Path(scan_dir)
            if scan_path.exists():
                for git_dir in scan_path.glob("*/.git"):
                    repo_paths.append(git_dir.parent)
    if repo_paths:
        # Deduplicate
        repo_paths = list({p.resolve(): p for p in repo_paths}.values())
        print(f"Scanning {len(repo_paths)} git repo(s)...")
        evidence["git"] = scan_repos(repo_paths, max_commits=args.max_commits)
        ai_total = 0
        for repo in evidence["git"]:
            if repo.get("found"):
                ai_total += repo['ai_coauthored_commits']
        found = sum(1 for r in evidence["git"] if r.get("found"))
        print(f"  {found} repos scanned, {ai_total} AI co-authored commits total")


    # Filter to top N projects if requested
    if args.top_projects > 0:
        for source_key in ("claude_code", "claude_ai"):
            if source_key not in evidence or not evidence[source_key].get("samples"):
                continue
            samples = evidence[source_key]["samples"]
            project_counts = Counter(s["project"] for s in samples)
            top = [p for p, _ in project_counts.most_common(args.top_projects)]
            evidence[source_key]["samples"] = [s for s in samples if s["project"] in top]
            print(f"\n  [{source_key}] Top {args.top_projects} projects selected: {', '.join(top)}")
            print(f"    Filtered {len(samples)} -> {len(evidence[source_key]['samples'])} messages")

    # Save evidence
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2, default=str)
    print(f"\nEvidence saved to {evidence_path}")


def cmd_questionnaire(args: argparse.Namespace) -> None:
    """Run the self-assessment questionnaire."""
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = output_dir / EVIDENCE_FILE

    # Load existing evidence
    evidence = {}
    if evidence_path.exists():
        with open(evidence_path) as f:
            evidence = json.load(f)

    responses = run_questionnaire(interactive=True)
    evidence["questionnaire"] = format_questionnaire_results(responses)

    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2, default=str)
    print(f"\nQuestionnaire responses saved to {evidence_path}")


def cmd_report(args: argparse.Namespace) -> None:
    """Generate the assessment report from collected evidence."""
    output_dir = Path(args.output)
    evidence_path = output_dir / EVIDENCE_FILE

    if not evidence_path.exists():
        print("No evidence collected yet. Run 'collect' and/or 'questionnaire' first.")
        sys.exit(1)

    with open(evidence_path) as f:
        evidence = json.load(f)

    report_path = output_dir / REPORT_FILE
    report = generate_report(evidence, report_path)

    print(f"Report generated: {report_path}")
    print(f"Report size: {len(report)} characters")
    print(f"\nNext step: Open this report in Claude Code and ask for your assessment.")
    print(f"  Example: 'Read {report_path} and assess my AI fluency'")


def main():
    parser = argparse.ArgumentParser(
        description="Assess your AI fluency based on Anthropic's 4D framework"
    )
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT_DIR),
                        help="Output directory (default: .ai-fluency/)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # collect
    collect_parser = subparsers.add_parser("collect", help="Collect evidence from AI activity")
    collect_parser.add_argument("--claude-export", "-c",
                                help="Path to Claude.ai export directory or conversations.json")
    collect_parser.add_argument("--claude-code-dir",
                                help="Path to Claude Code projects dir (default: ~/.claude/projects/)")
    collect_parser.add_argument("--skip-claude-code", action="store_true",
                                help="Skip Claude Code session scanning")
    collect_parser.add_argument("--repos", "-r", nargs="+",
                                help="Git repository paths to scan")
    collect_parser.add_argument("--scan-dirs", "-d", nargs="+",
                                help="Directories to scan for git repos (scans one level deep)")
    collect_parser.add_argument("--max-sessions", type=int, default=50,
                                help="Max Claude Code sessions to scan (default: 50)")
    collect_parser.add_argument("--max-commits", type=int, default=200,
                                help="Max commits per repo to scan (default: 200)")
    collect_parser.add_argument("--top-projects", type=int, default=0,
                                help="Only include top N projects by message count (0 = all)")

    # questionnaire
    subparsers.add_parser("questionnaire", help="Run the self-assessment questionnaire")

    # report
    subparsers.add_parser("report", help="Generate the assessment report")

    args = parser.parse_args()

    if args.command == "collect":
        cmd_collect(args)
    elif args.command == "questionnaire":
        cmd_questionnaire(args)
    elif args.command == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
