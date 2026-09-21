# MQ-5.ER Real-Artifact Encoding Verification

Status:

**IMPLEMENTED / NOT YET EXECUTED**

## Purpose

Verify the MQ-5.ER encoder variants using the real frozen retinal-territory
artifact and the frozen 192-frame synthetic Condition-A episode before any
connectome or neural-runtime execution is authorized.

This is an encoding-only gate.

## Required checks

The verifier must fail closed unless:

- the normalized episode contains the frozen 12 observations;
- each observation produces 16 encoded frames;
- the complete episode contains exactly 192 frames;
- Arm A is byte-identical to the frozen `MarketVisionTemporalEncoder`;
- an independently rebuilt Arm A episode is byte-identical;
- Arms B, C, D, and E preserve the same nonzero retinal support as Arm A;
- every territory retains mean integrated energy equal to the frozen sensory
  gain within the predefined numerical tolerance;
- all alternative arms reproduce their own stimulus hashes deterministically;
- Arm D contains the complete frozen twelve-mapping family;
- Arm D identity mapping is byte-identical to Arm A.

## Explicit exclusions

The verifier does not:

- load the connectome;
- instantiate any neural runtime;
- inspect responder activity;
- calculate neural outcome metrics;
- classify MQ-5.ER scientific outcomes.

Therefore its output is implementation-verification evidence, not an
MQ-5.ER result.

## Artifact

The verifier writes:

`artifacts/mq5-er-encoding-real-artifact-verification-v1.json`

The artifact records hashes and encoding diagnostics only.

It must not be overwritten silently.

## Next gate

Only after this verification passes may the project freeze response-preservation
tolerances and prepare the result-bearing neural runner.

Financial semantics remain:

**NOT ASSIGNED**
