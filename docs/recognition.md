# Recognition

Recognition compares a selected current synthetic observation with a selected represented supporting record under a versioned equality rule.

The implemented state subset is:

- `BASIS_CORRESPONDS`
- `CHANGED_CORRESPONDENCE`

Each RecognitionResult preserves profile and rule versions, selectors, source fact and record references, values, comparison outcome, state, and bounded interpretation. This is reference lineage, not verified source provenance.

The result establishes only whether the represented values satisfy the configured equality relationship. It does not establish validity, correctness, authority, required review, or a required response.
