# MoscaQuant Known Confounds Register

Status values:

- `OPEN`
- `OPEN — PARTIALLY MITIGATED`
- `OPEN — SUBSTANTIALLY MITIGATED`
- `MITIGATED`
- `RESOLVED`

The graded `OPEN` statuses indicate that evidence has narrowed a confound
without eliminating the remaining limitation.

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

Status: `OPEN — SUBSTANTIALLY MITIGATED`

Validated causal behavior has primarily been observed using the current
MoscaQuant simulation implementation.

A result reproduced only by one implementation may include
implementation-specific behavior.

Evidence to date:

- MQ-5.6 reproduced selected direct-edge, two-hop pathway, and convergence
  findings using an independently implemented full-network reference runtime.
- All predefined numerical and qualitative replication gates passed.
- The independent runtime did not inherit from or call the production neural
  runtime or MQ-5 intervention runtime.

Remaining limitation:

- independent replication currently covers a selected frozen causal subset,
  not the entire validated population or every experimental condition.

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

Status: `OPEN — PARTIALLY MITIGATED`

Market-to-sensory encoding is an experimental design choice.

Evidence to date:

- CONF-004A showed that the principal MQ-5 causal findings survived
  replacement of causal rolling mean/std normalization with causal
  rolling median/MAD normalization.
- Generalized single-node, pathway, and convergence findings retained
  their qualitative structure.
- This mitigates dependence on the normalization choice specifically.

Remaining untested encoding components include:

- retinal territory assignment
- temporal motion encoding
- volatility-dependent cadence
- entropy-dependent temporal jitter
- sensory gain
- broader representation changes

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

### MQ-5.ER update — broader encoding robustness

MQ-5.ER materially expanded CONF-004 beyond the prior normalization-only test.

Frozen result:

- fixed cadence: response retained with altered expression;
- zero entropy-dependent temporal jitter: response pattern not retained;
- all eleven balanced non-identity asset/ticker-to-retinal-territory remaps:
  response pattern preserved;
- no momentum-dependent temporal motion: response retained with altered
  expression.

The no-jitter arm retained all nine frozen responders but lost the accepted
13-edge bundle-level causal effect for five targets (`55`, `92`, `656`,
`126002`, `137122`).

**CONF-004 therefore remains OPEN.** The confound is now substantially
characterized rather than eliminated: some tested encoding choices are robust,
while at least one tested temporal-irregularity encoding choice changes the
accepted causal organization.

Still open include sensory-gain variation, broader representation families,
and the mechanistic identity of alternative routes recruited when
entropy-dependent temporal jitter is removed.

Result artifact SHA-256:

`737a316a98d91b95dc1a5fe3ac25e7bf229447ae422ecd23ecf39ea8d4f6bb39`

### MQ-5.ER.1 update — DETOUR route discovery

MQ-5.ER.1 followed the Arm-C no-jitter result with a frozen three-hop discovery
search over the five targets whose original 13-edge bundle dependence was no
longer expressed.

Frozen result:

- classification: `FOCUSED_DETOUR_CANDIDATES`;
- recurring directed edge: `116680 -> 12024`;
- affected-target recurrence: `92`, `656`, `137122`;
- retained-dependency comparison recurrence: `1273`.

This narrows the open mechanism question but does not eliminate CONF-004.
Because the same focused edge also appears in retained comparison target
`1273`, DETOUR does not establish that the candidate route is specific to the
encoding-induced bypass phenomenon.

**CONF-004 remains OPEN — substantially characterized, not eliminated.**

Still open include:

- prospective causal testing of the focused DETOUR edge;
- affected-target specificity versus broader shared-route use;
- sensory-gain variation;
- broader representation families.

Required confirmatory follow-up:

`MQ-5.ER.2 — ROADBLOCK`

DETOUR result SHA-256:

`4b06c0181514f01715319dfacfa91569202067e583db7ef9fda5f35818eb4611`

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

**Status: OPEN — SUBSTANTIALLY MITIGATED BY MQ-5.TS**

MQ-5.TS materially strengthens the topology-control record beyond the earlier
single shuffled-connectome family.

The completed benchmark compared Arm A against:

- SHUFFLED MOSCA v2 across `20 / 20` preregistered Arm B seeds; and
- a strict matched-topology Arm C null across `20 / 20` preregistered seeds.

Arm C preserved exact per-neuron directed degree, transmitter-sign structure,
the protected retinal interface, postsynaptic signed-weight structure, incoming
absolute normalization, edge count, duplicate exclusion, and no-new-self-edge
semantics.

Observed exact Arm-A response-pattern reproductions:

- Arm B: `0 / 20`;
- Arm C: `0 / 20`.

Preregistered classification:

`TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED`

This substantially mitigates the concern that topology-specific conclusions
depend on one weak or overly destructive randomization.

CONF-006 remains open because MQ-5.TS does not exhaust every scientifically
reasonable null family. Additional cell-class-, spatial-, motif-, or other
biologically constrained nulls may still be informative if separately
justified and preregistered.

The accepted MQ-5.TS result must not be generalized into a claim that every
alternative topology family has been excluded.

Evidence:

- `docs/experiments/mq5-ts-topology-specificity-protocol.md`
- `docs/experiments/mq5-ts-topology-specificity-results.md`
- artifact SHA-256: `903bff56fba99580b93db2a875f4c1996e3976a018bb26d306ef61baf73b2811`



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

Status: `OPEN — PARTIALLY MITIGATED`

Exact deterministic reruns establish software reproducibility.

They do not establish robustness across stochastic variation, input
variation, implementations, or populations.

Evidence to date:

- MQ-5.6 added independent-implementation replication for selected causal
  findings and reproduced them within predefined tolerances.
- This goes beyond identical-code deterministic reruns.

Remaining:

- stochastic multi-seed robustness if randomness is introduced
- broader input variation
- wider replication coverage
- population-level replication

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

## DETOUR retinal pre-cancellation scoring

**Status:** OPEN — methodological correction required before future DETOUR-style
candidate discovery.

MQ-5.ER.2 post-result audit demonstrated that DETOUR can nominate
retina-to-relay edges whose ordinary connectome contribution is later canceled
by the frozen retinal double-count-removal path.

Observed example:

- focused candidate: `116680 -> 12024`
- presynaptic endpoint: frozen retina
- postsynaptic endpoint: frozen relay
- THE RACKET causal-support classification:
  `RACKET_CAUSAL_SUPPORT_NOT_OBSERVED`

Matched-control edge `78481 -> 16087` had the same retina-to-relay structural
relationship and likewise produced no measurable intervention effect.

**Required correction:** future DETOUR-style discovery must measure net
effective runtime contribution after retinal cancellation, or explicitly
exclude ordinary retina-to-relay contributions that are deterministically
removed by the runtime. Pre-cancellation contribution alone is not sufficient
for candidate ranking.

This finding does not retroactively alter the frozen MQ-5.ER.1 DETOUR artifact
or MQ-5.ER.2 THE RACKET result.

### RETOUR correction result

MQ-5.ER.3 RETOUR implemented the correction required by the DETOUR retinal
pre-cancellation scoring confound.

Ordinary retina-to-relay candidate edges whose connectome weights exactly match
the frozen relay representation are excluded from candidate emission. The
preregistered negative controls `116680 -> 12024` and `78481 -> 16087` both
passed this rule with exact zero coefficient delta.

The correction removed `1732` dynamically eligible candidate checks in the
authoritative run, and the prior focused edge did not reappear.

**Status:** MITIGATED FOR RETOUR-STYLE CONNECTOME-EDGE DISCOVERY.

Remaining limitation: this does not test interventions on the frozen direct
retinal relay representation itself, and does not prove that newly identified
runtime-aligned candidates are causal. Those require separate preregistered
intervention experiments.
