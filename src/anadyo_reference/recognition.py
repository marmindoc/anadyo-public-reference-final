"""Bounded correspondence recognition for the public ANADYO reference."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from .neutral_facts import NeutralFact


BASIS_CORRESPONDS = "BASIS_CORRESPONDS"
CHANGED_CORRESPONDENCE = "CHANGED_CORRESPONDENCE"
SUPPORTED_STATES = {BASIS_CORRESPONDS, CHANGED_CORRESPONDENCE}


@dataclass(frozen=True)
class FactSelector:
    entity_id: str
    entity_type: str
    attribute: str

    def matches(self, fact: NeutralFact) -> bool:
        return (
            fact.entity_id == self.entity_id
            and fact.entity_type == self.entity_type
            and fact.attribute == self.attribute
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class RelationshipRule:
    rule_id: str
    rule_version: str
    relationship_type: str
    current_selector: FactSelector
    support_selector: FactSelector
    comparison: str


@dataclass(frozen=True)
class RelationshipProfile:
    profile_id: str
    profile_version: str
    rules: list[RelationshipRule]


@dataclass(frozen=True)
class RecognitionResult:
    recognition_id: str
    trace_id: str
    state: str
    relationship_profile_id: str
    relationship_profile_version: str
    rule_id: str
    rule_version: str
    relationship_type: str
    selectors: dict[str, dict[str, str]]
    source_fact_refs: list[str]
    source_record_refs: list[dict[str, str]]
    observed_values: dict[str, Any]
    comparison: dict[str, Any]
    interpretation: dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "recognition_id": self.recognition_id,
            "trace_id": self.trace_id,
            "state": self.state,
            "relationship_profile_id": self.relationship_profile_id,
            "relationship_profile_version": self.relationship_profile_version,
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "relationship_type": self.relationship_type,
            "selectors": self.selectors,
            "source_fact_refs": list(self.source_fact_refs),
            "source_record_refs": list(self.source_record_refs),
            "observed_values": dict(self.observed_values),
            "comparison": dict(self.comparison),
            "interpretation": {key: list(value) for key, value in self.interpretation.items()},
        }


def load_profile(raw_profile: dict[str, Any]) -> RelationshipProfile:
    rules = [
        RelationshipRule(
            rule_id=str(raw_rule["rule_id"]),
            rule_version=str(raw_rule["rule_version"]),
            relationship_type=str(raw_rule["relationship_type"]),
            current_selector=FactSelector(**raw_rule["current_selector"]),
            support_selector=FactSelector(**raw_rule["support_selector"]),
            comparison=str(raw_rule.get("comparison", "equals")),
        )
        for raw_rule in raw_profile.get("rules", [])
    ]
    return RelationshipProfile(
        profile_id=str(raw_profile["profile_id"]),
        profile_version=str(raw_profile["profile_version"]),
        rules=rules,
    )


def recognize(facts: list[NeutralFact], profile: RelationshipProfile) -> list[RecognitionResult]:
    results = []
    for rule in profile.rules:
        current = _one(facts, rule.current_selector, rule.rule_id, "current")
        support = _one(facts, rule.support_selector, rule.rule_id, "support")
        if current.trace_id != support.trace_id:
            raise ValueError(f"{rule.rule_id} source facts must share a trace_id")
        matched = _compare(current.observed_value, support.observed_value, rule.comparison)
        state = BASIS_CORRESPONDS if matched else CHANGED_CORRESPONDENCE
        observed_values = {"current": current.observed_value, "support": support.observed_value}
        results.append(
            RecognitionResult(
                recognition_id=_stable_id(
                    profile.profile_id,
                    profile.profile_version,
                    rule.rule_id,
                    rule.rule_version,
                    current.fact_id,
                    support.fact_id,
                    observed_values,
                    state,
                ),
                trace_id=current.trace_id,
                state=state,
                relationship_profile_id=profile.profile_id,
                relationship_profile_version=profile.profile_version,
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                relationship_type=rule.relationship_type,
                selectors={
                    "current": rule.current_selector.to_dict(),
                    "support": rule.support_selector.to_dict(),
                },
                source_fact_refs=[current.fact_id, support.fact_id],
                source_record_refs=[
                    {"side": "current", "source_id": current.source_id, "source_record_id": current.source_record_id},
                    {"side": "support", "source_id": support.source_id, "source_record_id": support.source_record_id},
                ],
                observed_values=observed_values,
                comparison={"operator": rule.comparison, "satisfied": matched},
                interpretation=_interpret(state),
            )
        )
    return results


def _interpret(state: str) -> dict[str, list[str]]:
    observed = [
        "A current synthetic observation and a represented supporting record were supplied.",
        "Their represented values were compared using the configured equality rule.",
    ]
    not_established = [
        "Complete evidence or complete operational reality.",
        "Universal validity or correctness of a downstream result.",
        "Continued authority or permissibility of continuation.",
    ]
    unresolved = [
        "Facts, records, and conditions outside the supplied synthetic inputs.",
        "The operational significance of the recognized correspondence state.",
    ]
    if state == BASIS_CORRESPONDS:
        established = [
            "The two represented values satisfy the configured equality relationship within the supplied synthetic facts and rule."
        ]
    elif state == CHANGED_CORRESPONDENCE:
        established = [
            "The two represented values do not satisfy the configured equality relationship within the supplied synthetic facts and rule."
        ]
        not_established.extend(
            [
                "Invalidity, incorrectness, or loss of authority.",
                "A need for reassessment, revalidation, stopping, or any required response.",
            ]
        )
    else:
        raise ValueError(f"unsupported recognition state: {state}")
    return {
        "observed": observed,
        "established": established,
        "not_established": not_established,
        "unresolved_or_not_observed": unresolved,
    }


def _one(facts: list[NeutralFact], selector: FactSelector, rule_id: str, side: str) -> NeutralFact:
    matches = [fact for fact in facts if selector.matches(fact)]
    if len(matches) != 1:
        raise ValueError(f"{rule_id}:{side} expected exactly one source fact, found {len(matches)}")
    return matches[0]


def _compare(left: Any, right: Any, comparison: str) -> bool:
    if comparison == "equals":
        return left == right
    raise ValueError(f"unsupported comparison: {comparison}")


def _stable_id(*parts: Any) -> str:
    payload = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"rr-{hashlib.sha256(payload).hexdigest()[:16]}"
