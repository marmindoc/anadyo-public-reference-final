"""Run the public ANADYO two-state synthetic reference demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .neutral_facts import parse_jsonl
from .output import build_information_output
from .recognition import load_profile, recognize
from .recognition_context import assemble_recognition_context


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
SCENARIOS = ["corresponding_basis", "changed_correspondence"]


def run_demo(scenario: str, output_dir: Path) -> dict[str, object]:
    artifacts = build_demo_artifacts(scenario)
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, payload in artifacts.items():
        _write_json(output_dir / filename, payload)
    return artifacts["information_output.json"]


def build_demo_artifacts(scenario: str) -> dict[str, object]:
    scenario_dir = EXAMPLES / scenario
    facts = parse_jsonl((scenario_dir / "neutral_facts.jsonl").read_text(encoding="utf-8"))
    raw_profile = json.loads((scenario_dir / "relationship_profile.json").read_text(encoding="utf-8"))
    profile = load_profile(raw_profile)
    results = recognize(facts, profile)
    recognition_context = assemble_recognition_context(results)
    information_output = build_information_output(
        scenario_id=scenario,
        results=results,
        recognition_context=recognition_context,
    )
    return {
        "neutral_facts.json": [fact.to_dict() for fact in facts],
        "recognition_results.json": [result.to_dict() for result in results],
        "recognition_context.json": recognition_context,
        "information_output.json": information_output,
    }


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the public ANADYO synthetic reference demo.")
    parser.add_argument("--scenario", choices=SCENARIOS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_demo(args.scenario, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
