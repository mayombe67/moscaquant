# Post-MQ-5 Topology-Specificity Benchmark — SHUFFLE THE DECK

**Status:** PRE-REGISTERED / NOT YET EXECUTED
**Scope:** frozen MoscaQuant computational model
**Financial semantics:** NOT ASSIGNED

## Question

Does the specific frozen MaleCNS wiring contribute to the accepted MQ-3.2 /
MQ-5 causal response beyond what is expected from carefully matched randomized
topologies?

This benchmark is a methodological hardening experiment. It does not reopen,
retune, or replace MQ-3.2 or MQ-5.

## Frozen experimental basis

The benchmark inherits without modification:

- Condition A stimulus construction and timing;
- frozen visual transduction;
- frozen release gain `0.9981738484618123`;
- frozen physiology-constrained graded population;
- frozen DN consensus and accepted MQ-3.2 responder set;
- accepted MQ-3.2 first-onset causal-path artifact;
- the production neural dynamics used by the accepted MQ-3.2 / MQ-5 line.

No arm may alter non-topological runtime parameters.

## Four-arm design

### Arm A — ORIGINAL

Run the frozen biological MaleCNS topology unchanged.

Purpose:

- authoritative reference response;
- responder identity, timing, voltage, and causal-path baseline.

### Arm B — LEGACY SHUFFLED MOSCA v2

Reuse the existing validated MQ-2.1 null family.

Construction:

- mapped R1-R6 presynaptic identities are fixed;
- the complete mapped retinal output interface is preserved;
- non-retinal presynaptic identities are permuted within frozen transmitter
  sign;
- postsynaptic row degree and row weight sequence are preserved;
- incoming absolute normalization is preserved;
- total edge count is preserved;
- the global outdegree distribution is preserved.

Important distinction:

SHUFFLED MOSCA v2 does **not** preserve each non-retinal neuron's individual
outdegree. Because presynaptic identity is reassigned by a sign-stratified
bijection, an individual neuron inherits the outgoing edge pattern of another
same-sign neuron.

Arm B provides continuity with the existing MQ-2.1 topology-control record.

### Arm C — STRICT MATCHED TOPOLOGY NULL

Construct a new directed edge-swap null with stronger structural matching than
Arm B.

Required invariants:

- all mapped R1-R6-originating edges remain exactly unchanged;
- every neuron's exact directed outdegree is preserved;
- every neuron's exact directed indegree is preserved;
- transmitter sign is preserved on every reassigned source;
- every postsynaptic neuron retains its original number of incoming positive
  and negative edges;
- every postsynaptic row retains its original signed weight multiset;
- incoming absolute normalization is therefore preserved;
- total edge count is preserved;
- no self-edge or duplicate edge may be introduced unless the original graph
  already contained that exact edge;
- the randomization seed is explicit and recorded.

Implementation rule:

For eligible non-retinal edges, use same-source-sign directed double-edge swaps:

`a -> x, b -> y  =>  a -> y, b -> x`

where `sign(a) == sign(b)`.

A proposed swap is rejected if it creates an invalid duplicate/self-edge under
the frozen graph rules.

Randomization strength is frozen before result-bearing execution:

- eligible edges are all non-retinal-origin edges available to Arm C;
- each Arm C seed must complete exactly one accepted swap per eligible edge,
  rounded down to an even count where required by the implementation;
- the maximum attempted swaps are `20 * target_accepted_swaps`;
- failure to reach the accepted-swap target is an implementation failure for
  that seed and stops result interpretation; the seed is not replaced.

After topology swaps are complete, assign each target row's original signed
weight multiset deterministically across its new same-sign presynaptic
endpoints. This preserves the target row's frozen signed weight distribution
without importing outcome information.

Arm C exists specifically to separate topology effects from differences in
individual degree sequence.

### Arm D — ACCEPTED CAUSAL-ROUTE LESION

Run the original biological topology with the frozen MQ-3.2 first-onset
causal-route edge set disabled.

The lesion set is the previously accepted causal artifact. No new route search
or result-dependent target selection is allowed.

Purpose:

- positive intervention control;
- verify that the benchmark metrics detect disruption when an already accepted
  causal route is removed.

## Companion biological comparator — MQ-5.TS.BIO / THE OTHER DECK

MQ-002 / LILITH is required as a follow-on biological comparator, but she is
not a randomized null arm and does not participate in the A-vs-C
topology-specificity classification.

Scientific question:

> Where the accepted MQ-001 causal system has a valid official cross-matched
> analogue in MQ-002, does the same response organization transfer to an
> independently reconstructed biological topology?

This companion comparison must obey the existing MQ-002 qualification boundary:

- use only official MaleCNS / FlyWire cross-matched anatomy;
- do not infer or manufacture unavailable female optic-lobe or VNC anatomy;
- do not transform MORTY into LILITH or treat LILITH as a shuffled control;
- preserve identical non-connectomic runtime parameters wherever the compared
  substrate is genuinely matched;
- report unmatched or only partially matched causal elements explicitly rather
  than filling them in;
- no financial or trading semantics.

The companion analysis is conditional on a pre-execution route-mapping audit.

The audit must classify every accepted MQ-3.2 causal edge as exactly one of:

- `FULLY_CROSS_MATCHED`;
- `PARTIALLY_CROSS_MATCHED`;
- `UNAVAILABLE_IN_COMPARISON_PRODUCT`.

Only the fully cross-matched subset may enter direct MORTY-vs-LILITH dynamic
comparison.

If no scientifically meaningful fully cross-matched causal substrate exists,
MQ-5.TS.BIO stops with a qualification result. That outcome is retained and no
replacement anatomy is invented.

The companion comparison requires its own frozen result artifact and provenance
record. It may reuse the already frozen metrics where they remain semantically
valid, but it may not alter the primary Arm A/B/C/D protocol after those results
are seen.

## Randomization

Arm A and Arm D are deterministic single-topology arms.

Before randomized arms are interpreted, Arm A and Arm D each require exact
duplicate replay under the existing deterministic runtime contract.

Arm B and Arm C are randomized null ensembles.

Precommitted ensemble size:

- Arm B: 20 seeds
- Arm C: 20 seeds

Precommitted seeds:

- Arm B: `20262000` through `20262019`
- Arm C: `20263000` through `20263019`

This is the initial strict-null benchmark, not a population-level significance
claim. A larger independent replication, if scientifically warranted, requires
a separately frozen protocol and entirely new seeds before execution.

Rules:

- no seed selection after results;
- no early stopping;
- every precommitted seed must be evaluated;
- failed builds are recorded and investigated, not silently replaced;
- Arm B and Arm C use disjoint seed ranges;
- randomized connectomes may be built in memory and discarded after metrics and
  provenance are recorded.

## Primary metrics

The following metrics are frozen before result-bearing execution.

### 1. Responder identity

For the accepted MQ-3.2 DN-C1 responder universe, record which responders show
positive voltage under the same frozen criterion used by the accepted causal
line.

Compare each arm with Arm A using:

- responder count;
- exact responder-set identity;
- Jaccard overlap with Arm A.

### 2. First-onset timing

For every accepted responder, record the first positive-voltage frame.

Compare with Arm A using:

- exact onset agreement count;
- median absolute onset shift among responders present in both arms;
- maximum absolute onset shift among responders present in both arms.

Absent responders remain absent; they are not assigned an artificial onset.

### 3. Responder-voltage fingerprint

For the accepted responder set, construct one deterministic vector containing
the complete positive-voltage trajectory over the frozen 192-frame episode.

Compare each arm with Arm A using:

- cosine similarity;
- normalized L2 distance;
- maximum absolute voltage difference.

No post-result responder subset may be substituted.

### 4. Stimulus-to-DN information

Use a frozen scalar stimulus trace equal to the per-frame mean positive retinal
stimulus delivered to the mapped R1-R6 population.

Use a frozen scalar DN trace equal to the per-frame mean positive voltage over
the accepted MQ-3.2 responder set.

Estimate discrete mutual information with:

- 8 fixed-width stimulus bins over `[0, 1]`;
- 8 fixed-width DN bins over `[0, 1]`;
- DN values below 0 clipped to 0;
- DN values above 1 clipped to 1;
- lags `0, 1, 2, 3, 4`;
- report MI at every lag and the maximum across the frozen lag set.

The bin count and lag set may not be changed after results are inspected.

Mutual information is a predefined descriptive diagnostic. It may support
interpretation, but it may not by itself determine the topology-specificity
classification because the 192-frame trace is short and zero-heavy.

This is a model-level information diagnostic, not a claim about biological
coding or cognition.

### 5. Accepted causal-path survival

For each of the 13 frozen MQ-3.2 first-onset causal edges, record whether that
directed edge still exists in the tested topology.

Report:

- surviving causal-edge count;
- causal-edge survival fraction;
- whether the complete accepted causal route set survives.

Arm D is expected by construction to have zero survival for the lesioned edge
set and is therefore a positive intervention control, not a randomized null.

## Secondary diagnostics

Record for provenance and interpretation:

- total edge count;
- per-neuron indegree equality to Arm A;
- per-neuron outdegree equality to Arm A;
- incoming sign-count equality to Arm A;
- row signed-weight-multiset equality to Arm A;
- retinal-interface equality to Arm A;
- connectome logical hash;
- randomization seed;
- build rejection / accepted-swap counts for Arm C;
- runtime duration.

These diagnostics do not replace the primary metrics.

## Precommitted comparisons

The benchmark asks four separate questions.

### A vs B

Does the accepted response differ from the existing SHUFFLED MOSCA v2 null
family?

This comparison extends the earlier MQ-2.1 control into the accepted MQ-3.2 /
MQ-5 causal-response regime.

### A vs C

Does the accepted response differ from a null that preserves each neuron's
exact directed degree as well as transmitter sign, retinal interface, and
postsynaptic signed weight distribution?

This is the primary topology-specificity comparison.

### A vs D

Do the frozen metrics detect disruption when the already accepted causal route
is explicitly removed?

This is a positive intervention control and does not estimate a randomized null.

### A vs E — companion biological transfer

Where official cross-matching permits a valid comparison, does the accepted
MQ-001 causal organization transfer to MQ-002 / LILITH?

This comparison is descriptive biological-transfer testing, not a randomized
null and not evidence that either subject is superior.

It is reported separately from the Arm C topology-specificity classification.

## Interpretation rules

The benchmark uses a frozen descriptive classification rather than inventing a
post-result score.

For every Arm C seed define three response-pattern checks against Arm A:

1. responder-set identity matches Arm A exactly;
2. the first-onset vector over the accepted responder universe matches Arm A
   exactly, including absence where applicable;
3. normalized responder-voltage-fingerprint L2 distance is less than or equal
   to `1e-9`.

An Arm C seed counts as an exact response-pattern reproduction only if **all
three** checks match. A difference in any one check means that seed did not
reproduce the frozen Arm A response pattern.

The strict-null result is classified:

- `TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED` if at most `1 / 20` Arm C
  seeds exactly reproduce Arm A on all three checks;
- `MIXED TOPOLOGY SPECIFICITY` if `2 / 20` through `9 / 20` Arm C seeds exactly
  reproduce Arm A;
- `STRICT NULL FREQUENTLY REPRODUCES RESPONSE` if `10 / 20` or more Arm C seeds
  exactly reproduce Arm A.

These labels describe reproducibility of the accepted response pattern under
the frozen strict null. They do not establish biological optimality.

Arm B is reported separately for continuity with MQ-2.1 and cannot substitute
for Arm C.

Arm D is a positive intervention control. It must not be used to rescue a weak
or negative A-vs-C classification.

MQ-002 / LILITH is an independent biological comparator. Her result must not be
used to rescue, upgrade, or downgrade the A-vs-C strict-null classification.

Mutual information and causal-edge survival remain required primary diagnostics
but do not independently determine the classification.

No profitability, P&L, market prediction, or trading outcome is a metric in
this benchmark.

## Stop rules

Stop and report an implementation failure before result interpretation if:

- Arm C fails any frozen structural invariant;
- the retinal interface differs in any arm that is supposed to preserve it;
- any non-topological runtime parameter differs across arms;
- the accepted responder universe changes before execution;
- the frozen causal lesion set is regenerated rather than loaded from the
  accepted artifact;
- MQ-5.TS.BIO requires inferred, reconstructed, or manufactured anatomy outside
  the official cross-matched comparison products;
- any randomized ensemble is stopped early;
- any seed is dropped because its outcome is inconvenient.

## Claim boundary

A positive result supports only a statement about topology specificity inside
the frozen MoscaQuant computational model.

It does not establish:

- optimality of the MaleCNS connectome;
- biological superiority over randomized nervous systems;
- a universal property of Drosophila;
- consciousness, cognition, preference, or intent;
- financial usefulness;
- predictive trading value.

## Result artifact targets

Primary topology benchmark:

`${MOSCAQUANT_DATA_ROOT}/experiments/mq5-ts-topology-specificity-v1.json`

Companion biological-transfer audit/result:

`${MOSCAQUANT_DATA_ROOT}/experiments/mq5-ts-bio-other-deck-v1.json`

No result-bearing execution is authorized until this protocol and its control
configuration are committed.
