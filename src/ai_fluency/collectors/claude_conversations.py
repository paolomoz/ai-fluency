"""
Parse exported Claude.ai conversation JSON files.

Users can export their data from claude.ai Settings > Account > Export Data.
The export contains a conversations.json file with all conversations.
"""

import json
from pathlib import Path


def load_conversations(export_path: Path) -> list[dict]:
    """Load conversations from a Claude.ai export directory or JSON file."""
    if export_path.is_file() and export_path.suffix == ".json":
        with open(export_path) as f:
            data = json.load(f)
        return data if isinstance(data, list) else [data]

    # Look for conversations.json in export directory
    conv_file = export_path / "conversations.json"
    if not conv_file.exists():
        return []
    with open(conv_file) as f:
        return json.load(f)


def extract_user_messages(conversations: list[dict]) -> list[dict]:
    """Extract all human messages with conversation context."""
    messages = []
    for conv in conversations:
        conv_name = conv.get("name", conv.get("title", "Untitled"))
        conv_uuid = conv.get("uuid", conv.get("id", ""))
        chat_messages = conv.get("chat_messages", conv.get("messages", []))
        for msg in chat_messages:
            sender = msg.get("sender", msg.get("role", ""))
            if sender in ("human", "user"):
                text = ""
                # Handle different content formats
                content = msg.get("content", msg.get("text", ""))
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text = " ".join(
                        p.get("text", "") for p in content
                        if isinstance(p, dict) and p.get("type") == "text"
                    )
                if text.strip():
                    messages.append({
                        "source": "claude.ai",
                        "conversation": conv_name,
                        "conversation_id": conv_uuid,
                        "text": text.strip(),
                    })
    return messages


def analyze_conversations(export_path: Path) -> dict:
    """Analyze Claude.ai conversations and return evidence summary."""
    conversations = load_conversations(export_path)
    if not conversations:
        return {"source": "claude.ai", "found": False, "error": "No conversations found"}

    user_messages = extract_user_messages(conversations)
    total_conversations = len(conversations)
    total_messages = len(user_messages)

    # Gather raw message texts for the analyzer
    samples = []
    for msg in user_messages:
        samples.append({
            "conversation": msg["conversation"],
            "text": msg["text"][:2000],  # cap length for report
        })

    return {
        "source": "claude.ai",
        "found": True,
        "total_conversations": total_conversations,
        "total_user_messages": total_messages,
        "samples": samples,
    }
