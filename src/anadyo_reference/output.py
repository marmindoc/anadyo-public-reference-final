"""Public informational output assembly."""

from __future__ import annotations

from typing import Any

from .recognition import RecognitionResult


FORBIDDEN_OUTPUT_KEYS = {
    "action",
    "approve",
    "approval",
    "authority_change",
    "authority_mutation",
    "continuation_instruction",
    "deny",
    "denial",
    "execute",
    "execution_instruction",
    "hold",
    "pacing_instruction",
    "prioritization",
    "prioritize",
    "priority",
    "reassessment_requirement",
    "recommend",
    "recommendation",
    "validity_verdict",
    "workflow_control",
}


def build_information_output(
    *,
    scenario_id: str,
    results: list[RecognitionResult],
    recognition_context: dict[str, Any],
) -> dict[str, Any]:
    output = {
        "scenario_id": scenario_id,
        "output_purpose": "bounded_correspondence_recognition_information",
        "boundaries": {
            "informational_only": True,
            "qualification_authority": False,
            "execution_authority": False,
        },
        "recognition_context": recognition_context,
        "information_items": [
            {
                "item_id": f"info-{result.recognition_id}",
                "kind": "bounded_correspondence_recognition",
                "recognition_result_ref": result.recognition_id,
                "state": result.state,
                "source_fact_refs": list(result.source_fact_refs),
                "relationship_profile_id": result.relationship_profile_id,
                "relationship_profile_version": result.relationship_profile_version,
                "rule_id": result.rule_id,
                "rule_version": result.rule_version,
            }
            for result in results
        ],
    }
    _assert_information_boundary(output)
    return output


def _assert_information_boundary(value: Any) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_OUTPUT_KEYS & set(value)
        if forbidden:
            raise ValueError(f"forbidden authority/disposition fields emitted: {', '.join(sorted(forbidden))}")
        for child in value.values():
            _assert_information_boundary(child)
    elif isinstance(value, list):
        for child in value:
            _assert_information_boundary(child)
