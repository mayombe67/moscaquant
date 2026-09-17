# MQ-5.8 — MQ-5 Acceptance

Status:

**ACCEPTANCE REVIEW FROZEN — FINAL VERDICT PENDING**

## Purpose

MQ-5.8 is the formal closeout review for MQ-5.

It does not generate new scientific evidence.

It verifies that the completed MQ-5 work satisfies the frozen scientific,
reproducibility, visualization, provenance, and claim-boundary requirements
established by the MoscaQuant Charter and Roadmap.

No acceptance criterion may be weakened after review begins.

## Acceptance scope

MQ-5 consists of:

- MQ-5.1 — Experimental Protocol
- MQ-5.2 — Intervention Harness
- MQ-5.3 — Single-Node Perturbation
- MQ-5.4 — Pathway Perturbation
- MQ-5.5 — Sham and Specificity Tests
- CONF-004A — Sensory-normalization robustness
- MQ-5.6 — Replication and Stability
- MQ-5.7 — Neuroscope Intervention Replay
- MQ-5.8 — Acceptance

## Required evidence

### 1. Protocol discipline

Acceptance requires evidence that:

- intervention semantics were frozen before outcome interpretation,
- attenuation levels were predefined,
- causal nodes and frames were frozen from prior evidence,
- matched and timing controls were prospectively defined where valid,
- pathway and convergence targets were preregistered,
- MQ-5.6 numerical tolerances were frozen before independent-runtime
  replication outcomes,
- MQ-5.7 was preregistered as read-only visualization.

### 2. Generalized single-edge intervention

Acceptance requires:

- all 13 frozen causal edges completed,
- all 13 retained monotonic dose-response behavior,
- sham behavior was verified,
- intervention telemetry was verified,
- deterministic full-silence reruns reproduced exactly,
- 12 / 12 edges with valid frozen matched controls showed a larger causal
  intervention effect than the matched control.

Timing-control results must be retained without claim inflation:

- 3 / 13 causal-frame interventions exceeded nearby timing controls,
- 10 / 13 nearby timing controls produced equal or larger effect magnitude,
- 7 / 13 full-silencing interventions delayed first positive downstream
  response.

Supported interpretation:

Frozen causal frames identify onset or evidence points within broader active
causal windows.

Unsupported interpretation:

Frozen causal frames are uniquely or temporally exclusive causal instants.

### 3. Multi-hop pathway

Acceptance requires the frozen pathway:

`56393 → 68045 → 1273`

to retain intervention propagation under:

- upstream attenuation,
- intermediate attenuation,
- predefined dose levels,
- frozen causal-frame semantics.

The result may support propagation within the frozen simulation model.

It must not be rewritten as biological pathway causality.

### 4. Convergence

Acceptance requires all frozen convergence systems:

- `44274 + 55925 → 55`
- `55548 + 87441 → 51`
- `92657 + 93484 → 129`

to retain:

- measurable contribution from each input,
- combined intervention exceeding either single intervention,
- monotonic combined-dose behavior.

No statistical synergy, antagonism, subadditivity, or superadditivity claim
is accepted without a separately preregistered interaction analysis.

Responder 51 must retain its numerical-scale caveat.

### 5. Sensory-normalization robustness

Acceptance requires CONF-004A to show that the principal MQ-5 findings were
retained under the frozen causal median / MAD normalization alternative.

This supports robustness to the tested normalization change only.

It does not establish general encoding independence.

### 6. Independent-runtime replication

Acceptance requires selected direct-edge, pathway, and convergence findings
to reproduce under the separately implemented full-network reference
runtime within the predefined numerical tolerances.

The independent reference runtime must not:

- inherit from the production neural runtime,
- call production `step()`,
- call production `effective_activity()`,
- call the MQ-5 intervention runtime.

This is independent implementation replication within the same frozen
mathematical model.

It is not biological replication.

### 7. Neuroscope replay boundary

Acceptance requires MQ-5.7 to:

- consume completed frozen artifacts,
- remain read-only,
- disable simulation feedback,
- generate no scientific outcomes,
- import no production neural runtime,
- import no MQ-5 intervention runtime,
- preserve existing anatomy / topology-fallback semantics,
- display missing telemetry as unavailable rather than reconstructing it,
- preserve responder-51 numerical-scale warnings,
- preserve non-synergy interpretation language.

Neuroscope visualization must add no scientific evidence.

### 8. Frozen-artifact integrity

Acceptance requires no frozen experimental source artifact to have been
modified by MQ-5.7 replay export or visualization.

Generated replay artifacts are downstream representations only.

### 9. Confound accounting

The confound register must retain unresolved limitations.

Expected state includes:

- CONF-002 — runtime implementation dependence:
  `OPEN — SUBSTANTIALLY MITIGATED`
- CONF-004 — sensory encoding dependence:
  `OPEN — PARTIALLY MITIGATED`
- CONF-007 — deterministic reruns are not statistical replication:
  `OPEN — PARTIALLY MITIGATED`

No open confound is automatically resolved by MQ-5 acceptance.

### 10. Claim boundary

MQ-5 acceptance may support:

> Frozen MoscaQuant simulation interventions exhibit reproducible direct,
> multi-hop, and convergent causal effects under the tested controls,
> normalization alternative, and selected independent-runtime replication.

MQ-5 acceptance must not claim:

- biological causality in living Drosophila,
- general sensory-encoding independence,
- complete descending-neuron population validity,
- uniqueness against all appropriate topology/null-model families,
- predictive financial usefulness,
- trading profitability.

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Acceptance rule

MQ-5 may be marked:

**COMPLETE — ACCEPTED WITH DOCUMENTED LIMITATIONS**

only if all required implementation, provenance, artifact-integrity, and
claim-boundary checks pass.

A failed criterion must be documented rather than repaired by changing the
acceptance rule after inspection.
