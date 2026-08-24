from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any

from anadyo_reference.demo_runner import SCENARIOS, build_demo_artifacts
from anadyo_reference.neutral_facts import parse_jsonl
from anadyo_reference.output import FORBIDDEN_OUTPUT_KEYS, _assert_information_boundary
from anadyo_reference.recognition import (
    BASIS_CORRESPONDS,
    CHANGED_CORRESPONDENCE,
    SUPPORTED_STATES,
    load_profile,
    recognize,
)


ROOT = Path(__file__).resolve().parents[1]


class PublicReferenceTests(unittest.TestCase):
    def _scenario(self, name: str):
        scenario_dir = ROOT / "examples" / name
        facts = parse_jsonl((scenario_dir / "neutral_facts.jsonl").read_text(encoding="utf-8"))
        profile = load_profile(json.loads((scenario_dir / "relationship_profile.json").read_text(encoding="utf-8")))
        return facts, profile, recognize(facts, profile)

    def _generated(self, scenario: str) -> dict[str, Any]:
        return build_demo_artifacts(scenario)

    def test_corresponding_basis_is_explicit(self) -> None:
        _, _, results = self._scenario("corresponding_basis")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].state, BASIS_CORRESPONDS)
        self.assertTrue(results[0].comparison["satisfied"])

    def test_changed_correspondence_is_explicit(self) -> None:
        _, _, results = self._scenario("changed_correspondence")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].state, CHANGED_CORRESPONDENCE)
        self.assertFalse(results[0].comparison["satisfied"])

    def test_only_bounded_two_state_subset_is_implemented(self) -> None:
        self.assertEqual(SUPPORTED_STATES, {BASIS_CORRESPONDS, CHANGED_CORRESPONDENCE})
        states = {self._scenario(name)[2][0].state for name in SCENARIOS}
        self.assertEqual(states, SUPPORTED_STATES)

    def test_minimal_trace_is_complete_and_versioned(self) -> None:
        facts, profile, results = self._scenario("changed_correspondence")
        result = results[0]
        self.assertEqual(result.relationship_profile_id, profile.profile_id)
        self.assertEqual(result.relationship_profile_version, profile.profile_version)
        self.assertEqual(result.rule_id, profile.rules[0].rule_id)
        self.assertEqual(result.rule_version, profile.rules[0].rule_version)
        self.assertEqual(set(result.selectors), {"current", "support"})
        self.assertEqual(result.comparison, {"operator": "equals", "satisfied": False})
        self.assertEqual({ref["side"] for ref in result.source_record_refs}, {"current", "support"})
        self.assertEqual(set(result.source_fact_refs), {fact.fact_id for fact in facts})

    def test_fact_and_information_references_resolve(self) -> None:
        artifacts = self._generated("changed_correspondence")
        output = artifacts["information_output.json"]
        facts = artifacts["neutral_facts.json"]
        results = artifacts["recognition_results.json"]
        fact_ids = {fact["fact_id"] for fact in facts}
        result_ids = {result["recognition_id"] for result in results}
        self.assertTrue(set(results[0]["source_fact_refs"]).issubset(fact_ids))
        self.assertEqual({item["recognition_result_ref"] for item in output["information_items"]}, result_ids)
        self.assertEqual(set(output["recognition_context"]["recognition_result_refs"]), result_ids)

    def test_bounded_interpretation_is_present_for_both_states(self) -> None:
        expected = {"observed", "established", "not_established", "unresolved_or_not_observed"}
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                result = self._scenario(scenario)[2][0]
                self.assertEqual(set(result.interpretation), expected)
                self.assertTrue(all(result.interpretation[section] for section in expected))

    def test_replay_is_deterministic_for_all_generated_artifacts(self) -> None:
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                first = self._generated(scenario)
                second = self._generated(scenario)
                self.assertEqual(first, second)
                self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_no_generic_confidence_field_in_public_artifacts(self) -> None:
        for scenario in SCENARIOS:
            artifacts = self._generated(scenario)
            for filename, payload in artifacts.items():
                with self.subTest(scenario=scenario, artifact=filename):
                    self.assertNotIn("confidence", _all_keys(payload))

    def test_information_output_is_explicitly_non_authoritative(self) -> None:
        for scenario in SCENARIOS:
            output = self._generated(scenario)["information_output.json"]
            self.assertTrue(output["boundaries"]["informational_only"])
            self.assertFalse(output["boundaries"]["qualification_authority"])
            self.assertFalse(output["boundaries"]["execution_authority"])

    def test_generated_output_has_no_authority_or_disposition_fields(self) -> None:
        for scenario in SCENARIOS:
            artifacts = self._generated(scenario)
            for filename, payload in artifacts.items():
                with self.subTest(scenario=scenario, artifact=filename):
                    self.assertFalse(FORBIDDEN_OUTPUT_KEYS & _all_keys(payload))

    def test_boundary_enforcement_checks_nested_fields(self) -> None:
        for forbidden_key in FORBIDDEN_OUTPUT_KEYS:
            with self.subTest(forbidden_key=forbidden_key):
                with self.assertRaises(ValueError):
                    _assert_information_boundary({"nested": [{forbidden_key: "not allowed"}]})

    def test_generated_artifacts_conform_to_schemas(self) -> None:
        neutral_schema = _schema("neutral_fact.schema.json")
        result_schema = _schema("recognition_result.schema.json")
        output_schema = _schema("public_information_output.schema.json")
        for scenario in SCENARIOS:
            artifacts = self._generated(scenario)
            facts = artifacts["neutral_facts.json"]
            results = artifacts["recognition_results.json"]
            output = artifacts["information_output.json"]
            for fact in facts:
                _validate_schema(fact, neutral_schema, neutral_schema)
            for result in results:
                _validate_schema(result, result_schema, result_schema)
            _validate_schema(output, output_schema, output_schema)


def _schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def _all_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(_all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_all_keys(child))
    return keys


def _validate_schema(value: Any, schema: dict[str, Any], root: dict[str, Any]) -> None:
    """Validate the small JSON Schema subset used by this repository."""
    if "$ref" in schema:
        target: Any = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        _validate_schema(value, target, root)
        return
    if "const" in schema:
        assert value == schema["const"]
    if "enum" in schema:
        assert value in schema["enum"]
    expected_type = schema.get("type")
    if expected_type == "object":
        assert isinstance(value, dict)
        required = set(schema.get("required", []))
        assert required.issubset(value)
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            assert set(value).issubset(properties)
        for key, child in value.items():
            child_schema = properties.get(key, schema.get("additionalProperties", {}))
            if isinstance(child_schema, dict):
                _validate_schema(child, child_schema, root)
    elif expected_type == "array":
        assert isinstance(value, list)
        assert len(value) >= schema.get("minItems", 0)
        if "maxItems" in schema:
            assert len(value) <= schema["maxItems"]
        for child in value:
            _validate_schema(child, schema.get("items", {}), root)
    elif expected_type == "string":
        assert isinstance(value, str)
        assert len(value) >= schema.get("minLength", 0)
        if "pattern" in schema:
            assert re.search(schema["pattern"], value)
    elif expected_type == "integer":
        assert isinstance(value, int) and not isinstance(value, bool)
        assert value >= schema.get("minimum", value)
    elif expected_type == "boolean":
        assert isinstance(value, bool)


if __name__ == "__main__":
    unittest.main()
