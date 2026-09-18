# MQ-7 — SC-03 Live Plasticity Activation Results

Status:

**COMPLETED / END-TO-END ADAPTIVE PATH VALIDATED**

## Pre-registration

This experiment was preregistered in:

`docs/experiments/mq7-live-plasticity-activation-protocol.md`

before end-to-end activation results were generated.

## Purpose

Validate the complete protocol-controlled SC-03 BAD SYNAPSE path from:

D6 selection

through:

- neural credit assignment;
- unique-edge selection;
- persistent plasticity state;
- restart/replay persistence;
- real-connectome effect;
- frozen structural invariance.

## Activation gate

SC-03 remains subject to the D6 selector's explicit plasticity gate.

When:

`plasticity_active = false`

SC-03 remains selected but returns:

`NOT_APPLICABLE`

No reroll occurs.

When:

`plasticity_active = true`

SC-03 may proceed only when the observational credit system returns exactly
one unique eligible leader.

## Credit outcomes

The validated orchestration produces:

`NO_UPDATE_NO_ELIGIBLE_PATHWAY`

when no eligible recent causal pathway exists.

It produces:

`NO_UPDATE_AMBIGUOUS_CREDIT`

when multiple edges share the highest eligibility trace.

Only:

`ELIGIBLE`

with exactly one leader permits a plasticity update.

## Update mechanics

A successful SC-03 event applies the previously validated persistent update:

`current_multiplier = current_multiplier × 0.95`

subject to the cumulative floor:

`0.80`

The frozen baseline connectome is never rewritten.

## Persistence

Plasticity state is stored in Oracle `adaptation_state`.

Validated persisted information includes:

- edge identity;
- baseline artifact identity;
- baseline weight;
- cumulative multiplier;
- update count;
- most recent evidence reference;
- session information;
- recovery counter;
- state hash chain.

Restart preserves the plasticity state exactly.

Tampering with persisted plasticity state while retaining the original hash
is detected and rejected.

## Recovery

Persistent plasticity follows the preregistered deterministic recovery rule.

After five completed trading sessions without another update to the edge:

`multiplier = min(1.0, multiplier / 0.95)`

Recovery proceeds toward baseline without modifying the frozen connectome.

## Real-connectome end-to-end validation

The frozen causal edge:

`56393 → 68045`

was used for end-to-end validation.

The sequence was:

1. D6 selected SC-03 with protocol-controlled plasticity enabled.
2. Real connectome weight was used in observational credit assignment.
3. The edge became the unique eligible leader.
4. Persistent plasticity state was updated to `0.95`.
5. Oracle state was written to disk.
6. Oracle state was reloaded to simulate restart.
7. The persisted multiplier remained `0.95`.
8. The multiplier was applied to the real frozen edge.
9. The resulting postsynaptic contribution was exactly 5% below baseline
   within the frozen numerical tolerance.

## Structural invariance

After the complete end-to-end sequence:

- `connectome.data` was unchanged;
- `connectome.indices` was unchanged;
- `connectome.indptr` was unchanged.

Plasticity remains an overlay.

## Test result

Full test suite:

**121 passed**

## Result classification

SC-03 selector gating:

**SUPPORTED**

Observational neural credit assignment:

**SUPPORTED**

Ambiguity blocking:

**SUPPORTED**

No-evidence blocking:

**SUPPORTED**

Persistent bounded plasticity:

**SUPPORTED**

Cumulative 20% floor:

**SUPPORTED**

Deterministic recovery:

**SUPPORTED**

Persistence across restart:

**SUPPORTED**

Tamper detection:

**SUPPORTED**

Real-connectome adaptive effect:

**SUPPORTED**

Frozen structural invariance:

**SUPPORTED**

Protocol-controlled live plasticity mechanics:

**SUPPORTED**

Biological learning in living Drosophila:

**NOT CLAIMED**

Synaptic causation of financial loss:

**NOT CLAIMED**

Financial utility:

**NOT CLAIMED**

## Activation conclusion

The mechanics required for protocol-controlled SC-03 adaptive plasticity have
been validated end to end.

This result permits SC-03 plasticity to become an explicitly enabled
experimental runtime condition.

Plasticity must remain disabled by default unless the active experimental
configuration explicitly enables the frozen SC-03 protocol.

No implicit or automatic activation is permitted.
