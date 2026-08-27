# ANADYO

## What ANADYO inspects

ANADYO makes a defined evidence-to-support relationship inspectable:

```text
Current synthetic observation
↔ Represented supporting basis
↔ Configured correspondence condition
```

This repository is a deliberately minimal technical reference. It shows how supplied synthetic facts and an explicit rule can produce bounded correspondence recognition with traceable informational output.

## Intended use

This repository is a fixed, inspectable public release snapshot of the documented reference mechanism. The packaged examples, schemas, and tests define the supported inspection surface for this release. Modification, extension, and behavior under inputs outside that packaged surface are not established by this release.

## Why the relationship matters

Relevant observations, supporting records, assumptions, references, and review history may exist while their relationship remains fragmented or implicit. Making one configured relationship explicit lets an external reviewer see what was compared, what the comparison establishes, and what remains unresolved.

## The configured relationship

The examples compare a synthetic current owner value with the owner value in a represented supporting record. The configured condition is equality. The comparison does not independently establish whether either source is complete, accurate, authoritative, or operationally sufficient.

## What this repository implements

```text
Synthetic facts
→ configured relationship rule
→ explicit equality comparison
→ bounded correspondence recognition
→ traceable recognition context
→ informational output
```

The implementation is deterministic and supports exactly one rule type (`equals`) and two bounded states. It is not the complete ANADYO runtime-review model.

## Worked synthetic examples

- `corresponding_basis`: the two represented owner values are equal.
- `changed_correspondence`: the two represented owner values are unequal.

Both examples emit a `RecognitionResult`; a matching relationship never disappears into an empty result set.

## Recognition states

- `BASIS_CORRESPONDS`: the represented values satisfy the configured equality relationship.
- `CHANGED_CORRESPONDENCE`: the represented values do not satisfy the configured equality relationship.

This repository intentionally does not implement `MIXED_EVIDENCE` or `NO_VISIBLE_CURRENT_BASIS`.

## Bounded interpretation

Every result contains four structured sections:

- `observed`: inputs and comparison actually visible to this implementation.
- `established`: only the bounded equality outcome.
- `not_established`: conclusions the outcome must not be used to claim.
- `unresolved_or_not_observed`: context outside the supplied facts and rule.

## Trace and reference lineage

A result preserves the relationship profile and version, rule and version, both selectors, source fact IDs, supplied source-record references, observed values, comparison operator and result, and bounded state. These links provide reference lineage; they do not verify source provenance or source truth.

## Authority and epistemic boundaries

Recognition ≠ Qualification Authority ≠ Execution Authority.

Observed context ≠ complete operational reality.

Synthetic validation ≠ operational validation.

Conceptual relevance ≠ implemented capability.

ANADYO does not determine validity, invalidity, correctness, downstream decision quality, authority standing or loss, reassessment or revalidation requirements, permissibility of continuation, priority, recommended action, workflow pacing, governance disposition, or execution control.

## Synthetic-demonstrator limitations

The examples are synthetic. This repository does not establish production readiness, operational effectiveness, deployment at scale, statistical generalization, integration success, or verified provenance. Timestamps and source identifiers are represented inputs; this implementation does not independently validate them.

## Architecture

NeutralFacts are selected by a versioned relationship profile. Recognition applies the configured equality rule and emits one versioned, traceable result per rule. Recognition-context assembly groups result references and states. Information-output assembly exposes those references under explicit non-authority boundaries.

See `docs/architecture.md`, `docs/recognition.md`, and `docs/observer-boundary.md`.

## Quick start

Set the source path:

```bash
export PYTHONPATH=src
```

PowerShell:

```powershell
$env:PYTHONPATH="src"
```

Run either example:

```bash
python -m anadyo_reference.demo_runner --scenario corresponding_basis --output outputs/corresponding_basis
python -m anadyo_reference.demo_runner --scenario changed_correspondence --output outputs/changed_correspondence
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Tests and schemas

Tests cover both states, deterministic results, the minimal trace, bounded interpretation, reference integrity, absence of generic confidence, schema conformance, and generated-output authority boundaries. They characterize the packaged inspection surface; passing them does not establish behavior outside that surface or constitute operational validation. JSON Schemas describe NeutralFact, RecognitionResult, and public information output.

See `validation/PUBLIC_VALIDATION_SUMMARY.md` for the bounded validation scope.

## Relationship to the Mini Visual MVP

The Mini Visual MVP and this Public Technical Reference expose the same bounded recognition principle at different scopes. The Mini Visual MVP is the richer browser-facing synthetic demonstration, with seven scenarios, multiple recognition states, and guided visual behavior. This repository is deliberately narrower: it supplies a smaller correspondence mechanism, deterministic examples, schemas, tests, and explicit limitations.

Across both artifacts, correspondence recognition remains separate from qualification, disposition, and execution authority. This repository does not implement everything shown in the Mini Visual MVP, and the richer visual must not be read as evidence that those additional behaviors are implemented here.

Private evaluation work is separate and is not represented as validation evidence or results in this repository.

## Acknowledgement

With gratitude to Robert “Huck” Huckaby for a private pre-reveal peer assessment that pressure-tested how the Mini Visual MVP and Public Technical Reference might be interpreted in practice, particularly where precision could be granted authority beyond what the evidence establishes.

The final design decisions, claims, and responsibility remain mine.

## Rights and reuse

This repository is publicly visible for technical review and reference only. It is not open source, and no open-source or other software license is granted. No permission is granted to copy, modify, redistribute, use commercially, or create derivative works unless explicitly authorized by the rights holder.
