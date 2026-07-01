from __future__ import annotations

import re

RESERVED_CONTEXT_TAGS = [
    "system",
    "developer",
    "memory-context",
    "research-state",
    "evidence-context",
    "tool-output",
    "skill-context",
    "subagent-task",
]


def sanitize_untrusted_source_text(text: str) -> str:
    sanitized = text
    for tag in RESERVED_CONTEXT_TAGS:
        sanitized = re.sub(rf"</?\s*{re.escape(tag)}\s*>", "", sanitized, flags=re.IGNORECASE)
    return sanitized

