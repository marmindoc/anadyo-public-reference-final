# Architecture

ANADYO demonstrates a minimal inspectable information flow:

```text
Synthetic NeutralFacts
→ versioned relationship profile and rule
→ explicit equality comparison
→ bounded RecognitionResult
→ RecognitionContext
→ public informational output
```

Recognition emits a result for every configured rule, including when the represented basis corresponds. RecognitionContext groups deterministic result references and bounded states; it does not qualify a system or direct a response.

This public reference omits the richer mini visual MVP, private evaluation material, integrations, deployment layers, and production runtime claims.
