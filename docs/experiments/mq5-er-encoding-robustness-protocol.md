# MQ-5.ER — Encoding Robustness
# CHANGE THE TRANSLATOR

**Status:** PRE-REGISTERED DESIGN / IMPLEMENTATION NOT YET AUTHORIZED
**Scope:** frozen MoscaQuant computational model
**Financial semantics:** NOT ASSIGNED

## Question

Do the accepted MoscaQuant neural findings persist when reasonable
market-to-sensory encoding assumptions are changed while the neural substrate,
runtime dynamics, responder definitions, and outcome metrics remain frozen?

MQ-5.ER addresses the remaining sensory-encoding limitation recorded as
CONF-004.

It does not reopen or retune MQ-3, MQ-5, MQ-5.TS, or any accepted causal
artifact.

## Motivation

CONF-004A already showed that principal MQ-5 causal findings survived one
specific normalization substitution:

- causal rolling mean / standard deviation;
- replaced by causal rolling median / MAD.

That materially mitigated dependence on normalization choice.

It did not establish general encoding independence.

The remaining question is whether important findings depend on other
hand-designed components of the market-to-retina transformation.

## Experimental discipline

MQ-5.ER uses a **one-factor-at-a-time confirmatory design**.

Each confirmatory arm changes exactly one frozen encoding component relative
to Arm A unless a separately documented paired component is mathematically
inseparable.

No result-dependent retuning is permitted.

No failed encoding may be replaced by a friendlier alternative after outcome
inspection.

No new responder set may be selected from an alternative-encoding result.

## Frozen neural substrate

All arms hold constant:

- original MaleCNS connectome;
- frozen transmitter-sign assignment;
- physiology-constrained neural runtime;
- graded non-retinal transmission semantics;
- retinal spike-only semantics;
- frozen release gain `0.9981738484618123`;
- accepted MQ-3.2 responder universe;
- accepted MQ-3.2 first-onset causal-edge artifact;
- frame count `192`;
- intervention semantics where intervention replay is used;
- numerical comparison definitions;
- financial semantics = false.

No encoding arm may alter the connectome or neural-dynamics parameters.

## Reference arm

### Arm A — FROZEN ENCODER

Arm A reproduces the accepted market-to-sensory pipeline exactly.

It is the authoritative encoding reference.

The implementation phase must demonstrate deterministic duplicate replay of
Arm A before any alternative encoding result is interpreted.

## Confirmatory alternative encodings

The implementation phase must first audit the current encoder and verify that
each proposed arm can be implemented as a single isolated encoding change.

If a proposed arm cannot be isolated without changing another frozen component,
implementation must stop and the protocol must be amended before any
result-bearing run.

### Arm B — FIXED TEMPORAL CADENCE

Replace volatility-dependent temporal cadence with one deterministic fixed
cadence chosen prospectively from the frozen encoder's existing cadence domain.

Hold constant:

- normalized feature values;
- feature identities;
- retinal territories;
- motion rule;
- entropy-dependent jitter rule unless mathematically coupled to cadence;
- sensory gain;
- neural substrate.

Purpose:

Test whether accepted responses depend specifically on volatility controlling
the temporal sampling cadence.

The fixed cadence is frozen prospectively at `2.5` cycles per observation,
the midpoint of the existing `1.0` to `4.0` cadence domain and the value
corresponding to normalized volatility `0.0`.

### Arm C — ZERO ENTROPY JITTER

Disable only the entropy-dependent temporal jitter contribution by setting
its phase-jitter multiplier to exactly `0.0`. The normalized entropy feature
value itself remains unchanged.

Hold constant:

- base cadence;
- volatility-dependent cadence;
- normalized feature values;
- feature identities;
- retinal territories;
- motion rule;
- sensory gain;
- neural substrate.

Purpose:

Test whether fine temporal irregularity introduced by the entropy rule is
required for the accepted response.

If current implementation couples entropy jitter inseparably to another timing
rule, this arm must not execute until the coupling is explicitly resolved in
the protocol.

### Arm D — BALANCED ASSET/TICKER-TERRITORY REMAP FAMILY

Change only the assignment of the six asset/ticker rows to retinal territories.

The seven feature columns within every asset row remain unchanged.

Arm D reuses the frozen balanced twelve-mapping design already implemented by
the ticker/territory control:

- six rotations of identity;
- six rotations of reversed identity;
- identity serves as the reference member;
- eleven non-identity mappings are confirmatory alternatives;
- every mapping is a permutation of the six asset rows;
- across all twelve mappings, each asset appears in each territory exactly
  twice.

The remap family must:

- preserve the exact retinal population;
- preserve territory geometry and sizes;
- preserve all seven within-row feature values;
- preserve temporal encoding;
- preserve sensory gain;
- preserve the full twelve-mapping balanced design;
- avoid selecting or dropping mappings based on neural outcomes.

Purpose:

Test whether the accepted response depends on the hand-designed
asset/ticker-to-retinal-territory assignment.

Arm D is an encoding robustness test, not a topology null.

### Arm E — NO MOMENTUM-DEPENDENT TEMPORAL MOTION

Disable only the hand-designed temporal translation of momentum into coherent
horizontal motion.

The frozen encoder normally applies:

`1 + 0.25 * momentum * motion_phase * geometry.x`

before per-frame energy renormalization.

Arm E freezes:

`motion_weight = 1.0`

for every neuron and frame while leaving the normalized momentum feature itself
unchanged.

Hold constant:

- base spatial feature pattern;
- feature values and identities;
- retinal territories;
- volatility-dependent cadence;
- entropy-dependent jitter;
- spatial energy normalization;
- mean territory energy;
- sensory gain;
- neural substrate.

Purpose:

Test whether accepted responses require the specific momentum-to-horizontal-
motion encoding rule.

This arm does not claim to test every reasonable alternative motion encoding.

## Sensory gain

Sensory gain remains frozen in MQ-5.ER v1.

Global gain has already been separately interrogated in prior work and changing
gain inside this benchmark would confound representation robustness with global
drive.

A future gain-specific encoding experiment may be preregistered separately if
scientifically justified.

## Primary response metrics

Every arm is compared with Arm A using the already accepted response universe.

### 1. Responder identity

Report:

- responder count;
- exact responder-set identity;
- Jaccard similarity against Arm A.

No alternative responder subset may be selected after inspection.

### 2. First positive-voltage onset

For every accepted responder report:

- onset frame;
- absence where no positive response occurs;
- exact onset-vector agreement;
- median absolute onset shift among common responders;
- maximum absolute onset shift among common responders.

### 3. Responder-voltage fingerprint

Use the complete positive-voltage trajectory over all `192` frames for the
accepted responder universe.

Report:

- cosine similarity;
- normalized L2 distance;
- maximum absolute difference.

### 4. Accepted causal-route expression

For the 13 frozen MQ-3.2 causal relationships, report whether the accepted
downstream response remains observable under the alternative encoding.

This metric concerns expression of the already frozen route under altered
input encoding.

It does not redefine causal edges.

### 5. Stimulus-to-DN information diagnostic

Use the same frozen information diagnostic definition as MQ-5.TS where
applicable:

- per-frame scalar retinal stimulus;
- per-frame mean positive responder voltage;
- 8 fixed-width bins over `[0, 1]`;
- lags `0..4`;
- report every lag and the maximum.

This remains a model-level information diagnostic.

It is not a biological coding claim.

## Encoding-level diagnostics

Each alternative arm must also report, before neural interpretation:

- total retinal drive by frame;
- per-feature input trace identity;
- retinal population identity;
- territory sizes;
- nonzero retinal-drive count by frame;
- mean and maximum retinal drive;
- deterministic encoding artifact hash.

These diagnostics verify that an arm changed only the intended representation
component.

## Confirmatory targets

MQ-5.ER v1 evaluates preservation of the existing accepted response pattern.

It does not search for a different alternative-encoding response that happens
to look interesting.

The frozen reference targets are:

- the 9 accepted MQ-3.2 responders;
- the 13 accepted first-onset causal relationships;
- the accepted 192-frame evaluation episode.

## Arm D mapping-family classification

Arm D is classified across all eleven non-identity remaps:

- `ASSET-TERRITORY ROBUST ACROSS TESTED REMAPS`:
  all `11 / 11` satisfy the frozen response-preservation criteria;
- `MIXED ASSET-TERRITORY DEPENDENCE`:
  between `1 / 11` and `10 / 11` satisfy the criteria;
- `ASSET-TERRITORY ASSIGNMENT DEPENDENCE SUPPORTED`:
  `0 / 11` satisfy the criteria.

No remap may be dropped, replaced, or rerun with a different mapping because of
its neural outcome.

These labels describe only the frozen tested mapping family.

## Classification philosophy

MQ-5.ER must not reduce encoding robustness to a single permissive pass/fail
number.

Each alternative arm is classified independently.

### PRESERVED

An arm may be called `RESPONSE PATTERN PRESERVED` only if:

- responder-set identity is exact;
- all accepted responders remain present;
- no previously absent responder in the frozen universe becomes present;
- onset behavior remains within a preregistered implementation-level tolerance;
- voltage-fingerprint distance remains within a preregistered numerical
  tolerance;
- accepted causal-route expression remains present.

The exact onset and voltage tolerances must be frozen after implementation
verification but before result-bearing execution.

### ALTERED BUT RETAINED

An arm is `RESPONSE RETAINED WITH ALTERED EXPRESSION` if the accepted responder
identity and causal-route expression remain present but timing or voltage
fingerprint exceeds the frozen preservation tolerance.

### NOT RETAINED

An arm is `RESPONSE PATTERN NOT RETAINED` if accepted responder identity or
accepted causal-route expression fails.

A negative arm is retained as evidence of encoding dependence.

It must not be repaired by changing the encoder after inspection.

## Overall interpretation

MQ-5.ER supports broader encoding robustness only to the extent demonstrated by
the tested arms.

Examples:

- all tested arms preserve the response:
  supports robustness across those specific encoding alternatives;
- timing arms preserve but retinal remap fails:
  supports temporal robustness but spatial-assignment dependence;
- most arms fail:
  indicates strong encoding dependence;
- mixed outcomes:
  must be reported component by component.

No outcome establishes universal encoding independence.

## CONF-004 boundary

CONF-004 may be further mitigated by this benchmark.

It must remain open unless the project separately defines and satisfies a
stronger closure criterion.

MQ-5.ER v1 is not authorized to silently mark CONF-004 resolved.

## Biological and financial claim boundaries

MQ-5.ER does not establish:

- biological sensory coding in living Drosophila;
- ecological validity;
- visual realism;
- financial prediction;
- trading usefulness;
- profitability.

Financial semantics remain:

**NOT ASSIGNED**

## Stop conditions

Result-bearing execution must stop before interpretation if:

- Arm A fails deterministic replay;
- an alternative arm changes more than its authorized encoding component;
- the neural substrate hash changes;
- the responder universe changes in configuration;
- the frozen causal artifact changes;
- output metrics differ from the frozen implementation contract;
- any result-bearing arm is executed before implementation/configuration freeze.

A failed alternative arm is a result and is not a stop condition by itself.

## Required implementation phase

Before any result-bearing execution:

1. inventory the exact current market-to-sensory encoder;
2. map each proposed arm to exact code-level semantics;
3. determine whether B, C, D, and E are truly one-factor changes;
4. implement deterministic encoding-only fixtures;
5. verify the frozen Arm B cadence of `2.5` cycles;
6. verify the frozen twelve-mapping Arm D balanced asset/territory family;
7. verify Arm E's frozen `motion_weight = 1.0` semantics;
8. freeze preservation tolerances;
9. add tests proving held-constant components are unchanged;
10. commit implementation and configuration;
11. run Arm A duplicate replay;
12. only then authorize result-bearing alternative arms.

## Artifact plan

Protocol:

`docs/experiments/mq5-er-encoding-robustness-protocol.md`

Configuration:

`config/controls/mq5-er-encoding-robustness-v1.toml`

Planned result artifact:

`${MOSCAQUANT_DATA_ROOT}/experiments/mq5-er-encoding-robustness-v1.json`

## Current authorization

**PROTOCOL DESIGN ONLY**

No MQ-5.ER result-bearing run is authorized by this commit.

The next action is implementation-level encoder inventory and feasibility
mapping.

## Final result

MQ-5.ER completed under the frozen response-classification contract.

- Arm A: `RESPONSE PATTERN PRESERVED`
- Arm B: `RESPONSE RETAINED WITH ALTERED EXPRESSION`
- Arm C: `RESPONSE PATTERN NOT RETAINED`
- Arm D family: `ASSET-TERRITORY ROBUST ACROSS TESTED REMAPS`
- Arm E: `RESPONSE RETAINED WITH ALTERED EXPRESSION`

Arm C retained all nine frozen responders but lost frozen bundle-level causal
expression for targets `55`, `92`, `656`, `126002`, and `137122`.

All eleven non-identity Arm D confirmatory mappings were individually
`RESPONSE PATTERN PRESERVED`.

Authoritative result artifact SHA-256:

`737a316a98d91b95dc1a5fe3ac25e7bf229447ae422ecd23ecf39ea8d4f6bb39`

See `docs/experiments/mq5-er-encoding-robustness-results.md` for the formal
result summary and claim boundaries.
