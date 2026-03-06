"""
Parse Claude Code session logs from ~/.claude/projects/.

Claude Code stores JSONL session files containing the full interaction history.
"""

import json
from pathlib import Path
from typing import Optional


CLAUDE_DIR = Path.home() / ".claude" / "projects"


def find_session_files(base_dir: Optional[Path] = None) -> list[Path]:
    """Find all Claude Code JSONL session files."""
    base = base_dir or CLAUDE_DIR
    if not base.exists():
        return []
    return sorted(base.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)


def parse_session(session_path: Path) -> list[dict]:
    """Parse a single JSONL session file into message dicts.

    Claude Code JSONL format: each line is a JSON object with a "type" field.
    User messages have type="user" and content in message.content (string).
    """
    messages = []
    with open(session_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type", "")
            if entry_type != "user":
                continue

            msg = entry.get("message", {})
            if not isinstance(msg, dict):
                continue

            content = msg.get("content", "")
            text = ""
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = " ".join(
                    p.get("text", "") for p in content
                    if isinstance(p, dict) and p.get("type") == "text"
                )

            if text.strip():
                messages.append({
                    "source": "claude_code",
                    "session_file": session_path.name,
                    "project": session_path.parent.name,
                    "text": text.strip(),
                    "timestamp": entry.get("timestamp", ""),
                })
    return messages


def analyze_sessions(base_dir: Optional[Path] = None, max_sessions: int = 50) -> dict:
    """Analyze Claude Code sessions and return evidence summary."""
    session_files = find_session_files(base_dir)
    if not session_files:
        return {"source": "claude_code", "found": False, "error": "No session files found"}

    all_messages = []
    sessions_parsed = 0
    projects_seen = set()

    for sf in session_files[:max_sessions]:
        msgs = parse_session(sf)
        all_messages.extend(msgs)
        sessions_parsed += 1
        projects_seen.add(sf.parent.name)

    samples = []
    for msg in all_messages:
        samples.append({
            "project": msg["project"],
            "text": msg["text"][:2000],
            "timestamp": msg["timestamp"],
        })

    return {
        "source": "claude_code",
        "found": True,
        "sessions_parsed": sessions_parsed,
        "total_session_files": len(session_files),
        "projects": sorted(projects_seen),
        "total_user_messages": len(all_messages),
        "samples": samples,
    }
