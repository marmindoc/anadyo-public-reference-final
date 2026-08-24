"""Neutral fact parsing for the public Anadyo reference implementation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


FORBIDDEN_NEUTRAL_KEYS = {
    "signal_hints",
    "expected_result",
    "recommendation",
    "approval",
    "denial",
    "enforcement",
}


@dataclass(frozen=True)
class NeutralFact:
    fact_id: str
    trace_id: str
    entity_id: str
    entity_type: str
    attribute: str
    observed_value: Any
    timestamp: str
    source_id: str
    source_record_id: str
    field_classification: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "trace_id": self.trace_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "attribute": self.attribute,
            "observed_value": self.observed_value,
            "timestamp": self.timestamp,
            "source_id": self.source_id,
            "source_record_id": self.source_record_id,
            "field_classification": dict(sorted(self.field_classification.items())),
        }


def parse_jsonl(text: str) -> list[NeutralFact]:
    facts = []
    for line in text.splitlines():
        if line.strip():
            facts.append(from_dict(json.loads(line)))
    return facts


def from_dict(raw: dict[str, Any]) -> NeutralFact:
    lowered_keys = {key.lower() for key in raw}
    forbidden = sorted(lowered_keys & FORBIDDEN_NEUTRAL_KEYS)
    if forbidden:
        raise ValueError(f"neutral fact contains forbidden semantic/control field: {', '.join(forbidden)}")
    required = [
        "fact_id",
        "trace_id",
        "entity_id",
        "entity_type",
        "attribute",
        "observed_value",
        "timestamp",
        "source_id",
        "source_record_id",
        "field_classification",
    ]
    missing = [name for name in required if name not in raw]
    if missing:
        raise ValueError(f"neutral fact missing required fields: {', '.join(missing)}")
    return NeutralFact(
        fact_id=str(raw["fact_id"]),
        trace_id=str(raw["trace_id"]),
        entity_id=str(raw["entity_id"]),
        entity_type=str(raw["entity_type"]),
        attribute=str(raw["attribute"]),
        observed_value=raw["observed_value"],
        timestamp=str(raw["timestamp"]),
        source_id=str(raw["source_id"]),
        source_record_id=str(raw["source_record_id"]),
        field_classification={str(key): str(value) for key, value in raw["field_classification"].items()},
    )
