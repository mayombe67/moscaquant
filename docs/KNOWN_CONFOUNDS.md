# MoscaQuant Known Confounds Register

Status values:

- `OPEN`
- `MITIGATED`
- `RESOLVED`

This document records limitations that remain relevant even when an
experiment produces a positive result.

It is not a claims ledger.

A confound remains present until evidence explicitly mitigates or
resolves it.

---

## CONF-001 — Simulated rather than biological causality

Status: `OPEN`

MoscaQuant intervention results currently establish causal effects within
the frozen simulation model.

They do not establish equivalent causal relationships in a living
Drosophila nervous system.

Affected claims:

- biological interpretation
- neural realism
- external validity

Mitigation direction:

- independent runtime replication
- reduced-circuit validation
- comparison with biological literature or data where appropriate

---

## CONF-002 — Runtime implementation dependence

Status: `OPEN`

Validated causal behavior has primarily been observed using the current
MoscaQuant simulation implementation.

A result reproduced only by one implementation may include
implementation-specific behavior.

Affected claims:

- robustness
- generality of simulated causal findings

Mitigation direction:

- independent runtime implementation
- reduced-circuit cross-checks
- numerical consistency testing

---

## CONF-003 — Market input is currently synthetic

Status: `OPEN`

Current validated neural experiments use synthetic market-derived input
conditions rather than a frozen historical-market validation corpus.

Affected claims:

- market relevance
- prediction
- trading utility

Mitigation direction:

- future historical replay
- held-out market validation
- walk-forward evaluation

Financial semantics remain:

`NOT ASSIGNED`

---

## CONF-004 — Sensory encoding dependence

Status: `OPEN`

Market-to-sensory encoding is an experimental design choice.

Observed pathways may depend on the chosen encoding rather than represent
a general property of the connectome.

Affected claims:

- generality
- robustness
- financial interpretation

Mitigation direction:

- alternative pre-registered sensory encodings
- encoding-ablation experiments
- representation robustness tests

---

## CONF-005 — Limited causally validated descending-neuron subset

Status: `OPEN`

The frozen descending-neuron boundary contains substantially more neurons
than the currently validated responder ensemble.

Strong causal evidence for the responder ensemble must not be generalized
to every descending neuron.

Affected claims:

- population-level DN conclusions
- generalization beyond validated responders

Mitigation direction:

- expand pre-registered intervention coverage
- report validated and unvalidated populations separately

---

## CONF-006 — Null-model diversity is incomplete

Status: `OPEN`

Topology-related conclusions should not depend on only one randomized
control family.

Affected claims:

- topology specificity
- anatomical-network importance

Mitigation direction:

Evaluate multiple appropriate null families, potentially including:

- degree-preserving rewiring
- sign-preserving rewiring
- weight-distribution-preserving controls
- cell-class-constrained controls
- spatially constrained controls where appropriate

---

## CONF-007 — Deterministic reruns are not statistical replication

Status: `OPEN`

Exact deterministic reruns establish software reproducibility.

They do not establish robustness across stochastic variation, input
variation, implementations, or populations.

Affected claims:

- replication
- robustness

Mitigation direction:

- multi-seed experiments where randomness exists
- varied inputs
- independent runtime replication
- pre-registered robustness tests

---

## CONF-008 — Financial usefulness is unvalidated

Status: `OPEN`

No validated neuroscience result currently establishes predictive or
profitable trading performance.

Affected claims:

- trading signal quality
- financial utility
- profitability

Mitigation direction:

MQ-8.5 historical held-out financial validation and subsequent required
gates.

Financial semantics remain:

`NOT ASSIGNED`
