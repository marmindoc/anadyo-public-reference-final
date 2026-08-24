# Public Validation Summary

## Scope

The test suite covers the two supplied synthetic examples and the repository's implemented equality-reference semantics: explicit state recognition, deterministic output, trace completeness, bounded interpretation, reference integrity, schemas, absence of generic confidence, and informational-output boundaries.

## Evidence boundary

All validation evidence is generated from this repository's synthetic inputs. Synthetic validation is not operational validation. This summary contains no pilot, deployment, integration, production-readiness, or operational-effectiveness claim.

## Run

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

The test runner's result is authoritative for the checked-out revision; this document does not hard-code a passing-test count.
