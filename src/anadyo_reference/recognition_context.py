"""Recognition-context assembly for bounded public information output."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .recognition import RecognitionResult


def assemble_recognition_context(results: list[RecognitionResult]) -> dict[str, Any]:
    result_refs = [result.recognition_id for result in results]
    states = [result.state for result in results]
    payload = json.dumps([result_refs, states], separators=(",", ":")).encode("utf-8")
    return {
        "context_id": f"ctx-{hashlib.sha256(payload).hexdigest()[:16]}",
        "recognition_result_count": len(results),
        "recognition_result_refs": result_refs,
        "bounded_correspondence_states": states,
    }
