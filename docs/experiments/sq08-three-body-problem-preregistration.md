# SQ-08 — THREE BODY PROBLEM

## Status

PREREGISTRATION DRAFT

No result has been observed under this protocol.
No SQ-08 mechanistic interpretation is authorized until this document is frozen.

## Origin

SQ-08 follows the sealed SQ-07 — THE MAW exhaustive subset experiment.

Under the frozen RL layout, SQ-07 identified a unique inclusion-minimal
`EXACT_FULL13` recapitulator consisting of the complete frozen three-edge
RL group.

No strict submask of that three-edge group reached `EXACT_FULL13`.

The complete three-edge mask did.

All supersets containing that three-edge core also remained `EXACT_FULL13`
under the frozen SQ-07 classification.

SQ-08 does not re-test whether the three-edge core exists.

It asks why the complete three-edge configuration is required for exact
recapitulation under the frozen RL computational endpoint.

## Primary scientific question

What mechanistic structure causes the three frozen RL edges to behave as a
jointly required exact-recapitulation core?

Candidate explanations include, without privileging any before execution:

1. serial dependency;
2. parallel convergence;
3. thresholded joint influence;
4. state-dependent interaction;
5. another topology-supported interaction detectable in the frozen model.

These are candidate explanatory classes, not assumed mechanisms.

## Frozen three-edge universe

SQ-08 operates only on the three RL-group edges already frozen and
prospectively validated before this experiment.

The exact edge identities must be imported from the authoritative SQ-06 /
SQ-07 frozen configuration.

They must not be selected again from outcome data.

The frozen BODY mapping is:

- `BODY A = E10`
  - presynaptic neuron: `65084`
  - postsynaptic neuron / accepted responder: `137122`
  - matched sham edge: `65084 -> 369`

- `BODY B = E11`
  - presynaptic neuron: `128590`
  - postsynaptic neuron / accepted responder: `317`
  - matched sham edge: `128590 -> 5803`

- `BODY C = E12`
  - presynaptic neuron: `135589`
  - postsynaptic neuron / accepted responder: `126002`
  - matched sham edge: `135589 -> 3587`

The BODY labels preserve frozen SQ-07 source order:

`E10, E11, E12`

Therefore the SQ-08 bit ordering is permanently:

`A, B, C`

SQ-08 inherits the SQ-07 lesion-mask semantics:

- `0` means the frozen BODY edge is retained;
- `1` means the frozen BODY edge is zeroed.

Therefore the condition `101`, for example, means BODY A and BODY C are
zeroed while BODY B is retained.

The BODY labels create no biological or anatomical claim.

They must not be reordered after result inspection.

## Experimental conditions

All eight binary subsets of the frozen three-edge universe are required:

- `000`
- `001`
- `010`
- `011`
- `100`
- `101`
- `110`
- `111`

The binary ordering must be frozen before execution.

No condition may be added, removed, relabeled, or reordered after result
inspection.

## Primary endpoint

The existing frozen SQ-07 computational response representation remains the
authoritative endpoint unless a separately frozen amendment states otherwise.

The primary analysis must determine whether the internal response trajectories
of the eight conditions support a specific interaction structure capable of
explaining why only `111` reaches the previously established exact
recapitulation state.

The endpoint must not be replaced post hoc by whichever internal quantity
produces the cleanest story.

## Required mechanistic readouts

For every condition, preserve the same declared internal measurements so that
the following can be compared without post-result selection:

1. source-side state for each of BODY A, BODY B, and BODY C;
2. immediate postsynaptic response at each affected target;
3. declared downstream path / convergence-state measurements;
4. final frozen response fingerprint;
5. spike output if spike state is available in the authoritative runtime.

The exact neuron/state fields must be frozen before result execution.

## Spike boundary

SQ-08 must explicitly determine whether spike output is represented in the
authoritative runtime and stored result.

If spike state is available, report it for every preregistered condition.

If spike state is not part of the SQ-08 runtime/result schema, state that
explicitly.

Absence of a spike analysis must never be silently interpreted as zero spikes.

## Frozen interaction decomposition

SQ-08 uses the complete eight-condition Boolean cube as a preregistered
factorial decomposition.

For every declared vector-valued or time-resolved readout `Y`, define:

- `Y000` — all three frozen BODY edges retained;
- `Y100` — BODY A only;
- `Y010` — BODY B only;
- `Y001` — BODY C only;
- `Y110` — BODY A + BODY B;
- `Y101` — BODY A + BODY C;
- `Y011` — BODY B + BODY C;
- `Y111` — BODY A + BODY B + BODY C all zeroed.

The bit-to-edge mapping must be frozen before execution and must never be
permuted after result inspection.

### Main effects

Relative to `Y000`:

`M_A = Y100 - Y000`

`M_B = Y010 - Y000`

`M_C = Y001 - Y000`

### Pair interactions

The preregistered pairwise interaction terms are:

`I_AB = Y110 - Y100 - Y010 + Y000`

`I_AC = Y101 - Y100 - Y001 + Y000`

`I_BC = Y011 - Y010 - Y001 + Y000`

These terms measure departures from the frozen additive two-component model.

### Three-way interaction

The preregistered irreducible three-way interaction is:

`I_ABC = Y111 - Y110 - Y101 - Y011 + Y100 + Y010 + Y001 - Y000`

This quantity is the primary THREE BODY PROBLEM interaction term.

A non-zero `I_ABC` means that the complete three-component response cannot be
reconstructed from the baseline, individual effects, and pairwise interaction
terms alone under the declared readout.

It does not by itself establish a biological mechanism.
No mechanistic conclusion may be generalized beyond the frozen computational endpoint.

### Additive prediction

The no-interaction prediction for the complete triple is:

`Y111_additive = Y000 + M_A + M_B + M_C`

The pair-complete prediction is:

`Y111_pairwise = Y000 + M_A + M_B + M_C + I_AB + I_AC + I_BC`

By construction:

`Y111 - Y111_pairwise = I_ABC`

subject only to the frozen numerical comparison tolerance.

### Numerical zero contract

SQ-08 inherits the frozen SQ-07 primary-fingerprint exactness contract.

Authoritative response quantity:

`positive_membrane_voltage`

Authoritative per-episode fingerprint shape:

`192 x 1191`

Frozen exactness tolerances:

- symmetric normalized L2 distance: `<= 1e-9`;
- maximum absolute distance: `<= 1e-12`.

No minimum meaningful-effect floor is defined.

No post-result threshold may be introduced.

For the irreducible three-way term, SQ-08 does not compare `I_ABC` directly
against an all-zero anchor. Instead, it compares the observed complete-triple
response `Y111` with the preregistered pair-complete reconstruction
`Y111_pairwise`.

`THREE_WAY_EXACT_ZERO` is emitted iff both:

- `symmetric_normalized_l2(Y111, Y111_pairwise) <= 1e-9`; and
- `max_abs(Y111 - Y111_pairwise) <= 1e-12`.

Otherwise the analyzer emits:

`THREE_WAY_NONZERO`

Because:

`Y111 - Y111_pairwise = I_ABC`

this test is the frozen operational definition of a detectable irreducible
three-way interaction under the SQ-08 response representation.

The tolerances may not be changed after inspecting SQ-08 results.

For every declared readout, the analyzer must report:

- norm of each main effect;
- norm of each pair interaction;
- norm of the three-way interaction;
- deterministic zero/non-zero classification under the frozen tolerance;
- temporal location of the first declared non-zero interaction, when
  time-resolved measurements permit it.

No interaction term may be called zero merely because it is visually small.

## Mechanistic evidence hierarchy

SQ-08 distinguishes mathematical interaction from mechanistic interpretation.

### Level 1 — factorial structure

The eight-state decomposition determines whether the response contains:

- individual effects;
- pairwise interactions;
- an irreducible three-way interaction.

This level requires no anatomical interpretation.

### Level 2 — path localization

The same frozen decomposition is applied independently to each preregistered
internal readout along the declared source-to-downstream measurement path.

The analysis asks where interaction first becomes detectable.

A later interaction must not be projected backward onto an upstream structure
that did not exhibit it.

### Level 3 — topology compatibility

Serial or parallel-convergence language is permitted only when the frozen
connectome topology and the preregistered internal-state ordering support that
interpretation.

A response pattern alone is insufficient to label a mechanism serial or
parallel.

### Level 4 — endpoint relation

The analyzer compares the interaction structure with the already-frozen
`EXACT_FULL13` endpoint.

SQ-08 may determine that exact recapitulation requires the complete
three-component configuration.

It may not generalize that requirement beyond the frozen computational
endpoint.

## Mechanistic classification rules

The mechanistic labels below are compatibility statements, not biological
identifications.

### SERIAL_COMPATIBLE

May be emitted only if:

1. the frozen topology supplies an ordered path through the relevant
   components or their declared downstream states;
2. preregistered temporal/state measurements are consistent with that order;
3. loss of an upstream component suppresses the declared downstream
   propagation in the preregistered comparison;
4. the result is not contradicted by another required frozen readout.

### PARALLEL_CONVERGENCE_COMPATIBLE

May be emitted only if:

1. the frozen topology supplies distinct preregistered branches;
2. those branches converge on a common declared downstream measurement;
3. branch-specific effects remain distinguishable before convergence;
4. the complete three-component condition produces the preregistered
   convergence state required for exact recapitulation.

### JOINT_THRESHOLD_COMPATIBLE

May be emitted only if a quantitative threshold and its measured variable were
frozen before execution.

The label requires the strict subsets to remain on one side of that frozen
boundary while `111` crosses it.

No threshold may be created from the observed SQ-08 distribution.

### INTERACTION_DEPENDENT

May be emitted when the frozen analysis detects a non-zero `I_ABC` under the
preregistered numerical tolerance.

This means the complete response contains an irreducible three-component term
under the declared representation.

It does not determine the anatomical cause of that interaction.

### UNRESOLVED

Must be emitted when the frozen measurements do not uniquely support a
mechanistic interpretation.

Multiple compatible mechanistic descriptions must be reported explicitly
rather than resolved by narrative preference.

`UNRESOLVED` is scientifically acceptable.

## Primary SQ-08 outputs

The authoritative analyzer must emit, at minimum:

1. the frozen BODY A/B/C edge mapping;
2. all eight condition identities;
3. deterministic duplicate status;
4. main-effect norms;
5. pair-interaction norms;
6. three-way-interaction norm;
7. zero/non-zero decisions under the frozen tolerance;
8. path-localized interaction results;
9. spike status or explicit spike-unavailable status;
10. endpoint classification for all eight conditions;
11. mechanistic compatibility labels;
12. explicit claim-boundary statements.

The primary scientific result is not required to select a single mechanism.

## Interaction analysis

SQ-08 must explicitly compare:

- each single-edge condition;
- each two-edge condition;
- the complete three-edge condition;
- the intact / zero-edge condition.

Pair and triple interactions must be computed using a formula frozen before
execution.

The analysis must distinguish:

- absolute response magnitude;
- response direction;
- temporal trajectory;
- final endpoint classification.

A difference in one does not automatically imply a difference in the others.

## Prohibited claims

SQ-08 cannot by itself establish:

- consciousness;
- intention;
- perception;
- behavior;
- fear;
- choice;
- biological necessity outside the frozen model;
- biological sufficiency outside the frozen model;
- organism-level control;
- market prediction;
- financial value.

The three-edge computational core must not be described as a
"three-neuron control circuit" unless a later experiment independently supports
that claim.

## E04 boundary

SQ-08 is not an E04 experiment.

The LR nine-edge exact-recapitulation core and E04 remain a separate follow-up
question.

No conclusion about E04 may be inferred from SQ-08.

## Replication

Every frozen condition must use the same deterministic replication policy.

Duplicate runs must agree exactly on all fields declared deterministic by the
runtime contract.

Any deterministic mismatch invalidates mechanistic interpretation until
resolved.

## Stopping rule

SQ-08 stops after:

1. all eight preregistered conditions complete;
2. required deterministic replicates complete;
3. all frozen readouts are stored;
4. the preregistered analyzer produces one of the declared classifications;
5. independent verification is complete.

No additional conditions may be introduced after inspecting SQ-08 results.

Any new mechanistic hypothesis becomes a new experiment.

## Independent verification

The independent verifier must:

- consume frozen SQ-08 result artifacts;
- recompute the primary mechanistic classification;
- not import the primary SQ-08 analyzer;
- not import an SQ-06 or SQ-07 classifier as a substitute;
- verify all expected conditions;
- verify duplicate consistency;
- verify hashes and frozen configuration identity.

## Science / narrative separation

Narrative material may dramatize recorded SQ-08 events.

Narrative material must not create measurements, mechanisms, causal claims, or
experimental outcomes.

Canonical narrative roles remain:

- MORTY / MQ-001 — experimental subject and telemetry source;
- GLaDOS / ORACLE-01 — proposal and interpretation layer;
- Placeholder McDoctorate / SCIENCE-01 — skeptical scientific reviewer;
- Senator Armstrong / WARDEN-01 — authorization / containment authority;
- Hahn — HR / corporate-culture authority with no scientific authority.

Hahn may make irrelevant pickleball comparisons.

These comparisons have no evidentiary status.

## Narrative designation

SCP-style containment documentation mixed with first-contact / hard-science
paranoia is permitted in the retrospective layer.

The three frozen edges may be narratively designated:

- BODY A
- BODY B
- BODY C

Narrative terminology must remain visibly separated from scientific
terminology.

## Canonical rule

Science first.

Lulz a very close second.

## Frozen mechanistic readout topology

SQ-08 uses a preregistered layered readout hierarchy.

### L0 — intervention edges

- BODY A: `65084 -> 137122`
- BODY B: `128590 -> 317`
- BODY C: `135589 -> 126002`

### L1 — immediate responders

The immediate responder set is frozen as:

- BODY A responder: `137122`
- BODY B responder: `317`
- BODY C responder: `126002`

These identities are inherited from the frozen SQ-06 / SQ-07 edge registry.

### L2 — downstream structural branches

For each immediate responder, SQ-08 will derive the complete set of downstream
nodes reachable within at most four directed connectome hops.

The maximum hop depth is frozen at:

`4`

The topology derivation must use only the frozen connectome and BODY responder
identities.

SQ-08 outcome values, response amplitudes, interaction strengths, endpoint
classes, or spike results may not be used to add, remove, rank, or reorder
nodes in the structural branch sets.

Define:

- `branch_A` = nodes reachable from `137122` within <= 4 directed hops;
- `branch_B` = nodes reachable from `317` within <= 4 directed hops;
- `branch_C` = nodes reachable from `126002` within <= 4 directed hops.

### L3 — structural convergence sets

Pairwise convergence sets are defined structurally as:

- `AB = branch_A intersection branch_B`
- `AC = branch_A intersection branch_C`
- `BC = branch_B intersection branch_C`

The three-way convergence set is:

- `ABC = branch_A intersection branch_B intersection branch_C`

Membership is determined before SQ-08 result execution.

Structural convergence alone is not evidence of functional mediation or
mechanistic interaction.

### Temporal interaction localization

For every declared mechanistic node trajectory, SQ-08 evaluates the frozen
factorial decomposition across the complete Boolean cube.

The analyzer will report, where numerically defined:

- first frame of nonzero `M_A`;
- first frame of nonzero `M_B`;
- first frame of nonzero `M_C`;
- first frame of nonzero `I_AB`;
- first frame of nonzero `I_AC`;
- first frame of nonzero `I_BC`;
- first frame of nonzero `I_ABC`.

The earliest detected nonzero `I_ABC` is reported as an interaction-localization
observation only.

It does not by itself establish biological necessity, sufficiency, mediation,
consciousness, behavior, or organism-level control.

### Final response layer

The final response layer remains the frozen SQ-07 primary fingerprint:

- quantity: `positive_membrane_voltage`;
- shape: `192 x 1191`.

Spike state, channel spike count, and channel spike rate are preserved and
reported as secondary descriptive readouts.

## Pre-result topology amendment

The original cumulative <=4-hop structural rule was found, before SQ-08
outcome execution, to be structurally non-discriminating.

The authoritative amended mechanistic frontier is documented in:

`docs/experiments/sq08-three-body-problem-topology-amendment.md`

The primary structural convergence set is the frozen one-hop direct
three-way frontier containing exactly 18 nodes.

The original <=4-hop topology artifact remains preserved as calibration
provenance and must not be deleted or rewritten.

## Mechanistic observation timing

SQ-08 mechanistic state capture occurs immediately after each invocation of the
frozen physiology runtime `step()`.

At this observation point:

- synaptic propagation for the frame has completed;
- stimulus contribution has been applied;
- threshold crossing has been evaluated;
- the frame's spike state has been committed;
- neurons that fired have already had membrane voltage reset by the frozen
  runtime.

Therefore mechanistic voltage and spike trajectories are paired readouts.

A recorded post-step voltage at reset does not imply absence of activation when
the corresponding spike value is `1`.

SQ-08 must not infer framewise activation from voltage alone where spike state
is available.

The observer is passive: it may copy frozen runtime state after `step()` but
must not modify voltage, spikes, synaptic state, activity, stimulus, or
connectome state.
