# SQ-09 — PATTERN SCREAMER

## Status

EXPLORATORY RETROSPECTIVE RESULT

No new neural execution was performed for SQ-09.

PATTERN SCREAMER analyzes the already-authoritative SQ-08 — THREE BODY PROBLEM
evidence after observation of the SQ-08 result.

Its findings are therefore exploratory and may generate prospective hypotheses,
but they are not themselves a new confirmatory experiment.

## Origin

SQ-07 — THE MAW identified the complete three-edge RL group as the unique
inclusion-minimal RL `EXACT_FULL13` recapitulator:

`0000000000111`

SQ-08 — THREE BODY PROBLEM then tested whether those three edges exhibited an
irreducible three-way interaction.

The preregistered SQ-08 result was:

`THREE_WAY_EXACT_ZERO`

PATTERN SCREAMER asks what structure remains after the three-way hypothesis is
removed.

## Frozen BODY coordinates

The three RL edges are:

- BODY A: `65084 -> 137122`
- BODY B: `128590 -> 317`
- BODY C: `135589 -> 126002`

All three presynaptic source neurons are frozen Tm4 graded neurons:

- 65084: Tm4
- 128590: Tm4
- 135589: Tm4

The immediate responders are not members of the frozen graded population.

## Source-side limitation

A post-result contract audit established that SQ-08 did not preserve the
preregistered source-side state for BODY A, BODY B, or BODY C.

The source neurons are not members of the frozen DN consensus and therefore
cannot be reconstructed from the SQ-08 primary DN arrays.

Accordingly, PATTERN SCREAMER makes no direct claim about the source-side
dynamics of the three Tm4 neurons.

See:

`sq08-source-side-readout-deviation.md`

## Structural-null audit

The SQ-08 runtime does not algebraically force higher-order lesion interactions
to zero.

The frozen runtime contains:

- recurrent state propagation;
- graded subthreshold transmission;
- clipping;
- maximum operations;
- threshold firing;
- voltage reset.

Therefore a nonzero pairwise or three-way factorial interaction was possible
in principle.

The observed zero higher-order terms are not guaranteed by the general runtime
architecture alone.

## Numerical-zero audit

The authoritative SQ-08 evidence NPZ has SHA-256:

`e95f054e827cf1232ef72019692e4bcfc099214a654e1a3267f0f41cfc66abfb`

The post-result numerical audit promoted the stored float32 observations to
float64 before factorial arithmetic.

For all three preserved readout regions:

- primary DN field;
- BODY responders;
- 18-node frontier;

the three-way term became literal numerical zero:

`I_ABC = 0`

The same result was obtained using:

- canonical float64 evaluation;
- differently associated float64 evaluation; and
- extended-precision long-double evaluation.

The small nonzero residual observed under direct float32 arithmetic is
therefore attributable to finite-precision evaluation order, not evidence of a
small underlying third-order effect in the stored cube.

Numerical-zero audit SHA-256:

`96bbf398d45a5ca93bc39ed33e55397a008c68f72075000b3beff111cd5dc08f`

## Lower-order decomposition

After promotion before arithmetic, the primary DN field and BODY responder
readouts contain:

- `M_A != 0`
- `M_B != 0`
- `M_C != 0`
- `I_AB = 0`
- `I_AC = 0`
- `I_BC = 0`
- `I_ABC = 0`

The preserved response is therefore exactly additive with respect to the three
SQ-08 lesion coordinates.

The first nonzero frames were:

- BODY B: frame 124
- BODY A: frame 125
- BODY C: frame 127

These temporal differences are descriptive only.

No term is promoted to a preferred mechanism by this exploratory analysis.

Lower-order presence audit SHA-256:

`77cb9dde15e84c8727c02188af24e6887ae5cdbc783d1a8c5289f530390404fa`

## Support localization

The immediate responder identities were not discovered by PATTERN SCREAMER.

They were inherited from the already-frozen SQ-06 / SQ-07 edge registry:

- BODY A -> 137122
- BODY B -> 317
- BODY C -> 126002

The new retrospective observation is support confinement: within the preserved
1,191-neuron primary DN field, each main effect remained confined to its
inherited immediate responder.

Specifically:

- `M_A` changes exactly one DN: 137122
- `M_B` changes exactly one DN: 317
- `M_C` changes exactly one DN: 126002

For each term:

- the primary effect exactly equals the corresponding BODY-responder slice;
- no nonzero values occur outside the three BODY responders.

More specifically:

- BODY A affects only its immediate responder 137122;
- BODY B affects only its immediate responder 317;
- BODY C affects only its immediate responder 126002.

No preserved primary-DN effect propagates beyond those immediate responders.

Support audit SHA-256:

`4bf69c2e3faed923e806821991cd55dc9c9f414599b785916633bae8bd02fa8d`

## Frontier result

Across the frozen 18-node direct-convergence frontier:

- `M_A = 0`
- `M_B = 0`
- `M_C = 0`
- `I_AB = 0`
- `I_AC = 0`
- `I_BC = 0`
- `I_ABC = 0`

No lesion effect of any factorial order was observed in the preserved frontier
readout.

This is a statement about the frozen recorded state only.

It does not establish anatomical disconnection or absence of influence through
unmeasured state variables.

## Relation to SQ-07

SQ-07 classified a candidate fingerprint against the frozen INTACT and FULL13
references using two simultaneous numerical gates:

- symmetric normalized L2 <= `1e-9`;
- maximum absolute difference <= `1e-12`.

A retrospective closed-form audit now resolves why all three RL BODY edges were
required for `EXACT_FULL13`.

Because the preserved SQ-09 decomposition has:

- nonzero `M_A`, `M_B`, and `M_C`;
- literal-zero `I_AB`, `I_AC`, `I_BC`, and `I_ABC`;
- disjoint primary support for the three main effects;

any strict submask of `111` necessarily omits at least one nonzero local
contribution.

The smallest of the three main effects is BODY C, with maximum absolute
amplitude:

`2.9374905352597125e-07`

That is:

`293749.05352597125 x`

the frozen SQ-07 maximum-absolute tolerance of `1e-12`.

Therefore all seven strict RL submasks are excluded from `EXACT_FULL13` by the
max-absolute gate alone.

No interaction term is required to explain the three-edge inclusion-minimal
result.

Retrospective classifier-closure SHA-256:

`e8cd6e3aea9d2f5b81cf16d91ce4317a5da350f0c05010c92f4d9b1dc194358c`

Canonical short form:

`BOOKKEEPING_NOT_TEAMWORK`

SQ-07 classified a candidate fingerprint by exact comparison against the
frozen INTACT and FULL13 references.

Under RL, SQ-07 reported:

- `EXACT_INTACT`: 1024 masks
- `INTERMEDIATE`: 6144 masks
- `EXACT_FULL13`: 1024 masks

The unique inclusion-minimal RL FULL13 recapitulator was:

`0000000000111`

The other ten mask coordinates were the inactive LR group under the RL layout,
and SQ-07 reported complete inactive-subset closure.

The class-count structure is therefore consistent with the eight possible
states of the final three RL bits:

- one state corresponding to INTACT;
- six partial states corresponding to INTERMEDIATE;
- one complete three-edge state corresponding to FULL13;

each repeated across the `2^10 = 1024` irrelevant configurations of the
inactive group.

## Exploratory interpretation

The combined SQ-07 / SQ-08 / SQ-09 evidence supports a simpler explanation for
the apparent three-edge requirement.

The identities of the three immediate responders were inherited from the
frozen edge registry. PATTERN SCREAMER did not independently discover those
edge-to-responder assignments.

What the preserved evidence newly shows is that:

- each main effect is confined to its inherited responder in the primary DN
  field;
- the three preserved main effects combine additively;
- all pairwise interaction terms are literal zero;
- the three-way interaction term is literal zero.

The retrospective classifier-closure audit further shows that every strict RL
submask necessarily fails SQ-07's frozen `EXACT_FULL13` max-absolute gate.

Therefore:

"all three edges are required"

does not imply:

"all three edges cooperate."

The three-edge minimality is completely explained by an exact-reproduction
classifier requiring three separately nonzero, additive local contributions to
all be present.

No pairwise or irreducible three-way interaction is required to explain the
SQ-07 RL result.

Canonical short form:

`BOOKKEEPING_NOT_TEAMWORK`

## Claim boundary

PATTERN SCREAMER does not establish:

- the source-side dynamics of BODY A, BODY B, or BODY C;
- why the three Tm4 sources have the observed downstream effects;
- biological necessity or sufficiency;
- an organism-level circuit;
- behavior;
- cognition;
- consciousness;
- perception;
- financial predictive value.

The current result is a retrospective computational decomposition of already
preserved evidence.

## Next scientific question

The unresolved mechanistic question is now upstream:

Why does each of the three frozen Tm4 source neurons independently produce its
corresponding isolated responder effect?

Answering that question requires prospective preservation of source-side state,
including at minimum:

- source voltage;
- source spikes;
- effective graded activity;
- immediate responder voltage;
- immediate responder spikes;

under a newly frozen measurement contract.

No such execution is authorized by PATTERN SCREAMER.

## Engineering findings

### APOTHEOSIS #25 — Portable trust

External reproducibility requires completeness at the release boundary, not
only internally valid provenance.

The SQ-08 external review packet now enforces the presence and hash binding of
the authoritative evidence NPZ.

### APOTHEOSIS #26 — Preregistration-to-schema closure

Every required preregistered measurement must map to a machine-verifiable
evidence field or an explicitly declared deterministic derivation.

SQ-08 exposed this failure mode when source-side state was required in prose
but omitted from the frozen evidence schema.

## Canonical summary

Three edges with inherited responder identities.

Three nonzero local effects confined to those responders.

Zero pairwise interaction.

Zero three-way interaction.

Seven strict RL submasks excluded from `EXACT_FULL13`.

The weakest omitted contribution still exceeds the frozen max-absolute
classifier tolerance by approximately `293,749x`.

The apparent three-edge dependency is bookkeeping, not teamwork.

PATTERN SCREAMER converts the apparent three-body mystery into an additive
three-component computational result without promoting inherited responder
identity into a new discovery.

Science first.

Containment second.
