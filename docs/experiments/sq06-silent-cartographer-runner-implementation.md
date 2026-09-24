# SQ-06 — SILENT CARTOGRAPHER — Authoritative Runner + Result Schema

**Status:** IMPLEMENTATION REVIEW CANDIDATE — RESULT EXECUTION NOT AUTHORIZED

## Purpose

This gate wires the already-published SQ-06 preregistration into one deterministic
28-episode runner and a result-sidecar contract.

It does not change the experiment design.

## Episode plan

The seven preregistered arms are executed in frozen order. Each arm is crossed
with `LR` then `RL`, with two exact duplicate replays per arm/layout.

Total: **28 episodes**.

No randomized topology is built anywhere in SQ-06.

## Intervention construction

- `INTACT` reuses the frozen baseline.
- `FULL13_TARGETED` reuses the inherited SQ-05 / MQ-3.2 13-edge lesion.
- `FULL13_SHAM` reuses the frozen SQ-05 13-edge sham.
- the four subgroup arms use the frozen SQ-06 10-edge / 3-edge operator.

The SQ-06 preflight also invokes the frozen SQ-05 dependency verifier rather
than trusting the SQ-05 runner wrapper hash alone. This binds the transitive
neural-runtime substrate, including transmitter signs, relay and graded
artifacts, MQ5 runtime code, MQ3.2 intervention code, SQ-05 intervention
adapters, stimulus, core preregistration, and SQ-05 result schema.

Inherited SQ-05 provenance is retained, but the outer arm label in the SQ-06
manifest is normalized to the actual SQ-06 arm name (`FULL13_TARGETED` or
`FULL13_SHAM`) so historical labels cannot overwrite current arm identity.

Because the inherited SQ-05 verifier does not itself hash the two Python modules
directly instantiated by `run_episode`, SQ-06 additionally binds:

- `brain/physiology_constrained_visual_transduction.py`
- `brain/visual_transduction.py`

Their exact source hashes are checked during SQ-06 preflight and result
execution.

## Primary endpoint

The primary fingerprint remains the `192 x 1191` positive-membrane-voltage
matrix.

Exact reproduction remains:

- symmetric normalized L2 `<= 1e-9`;
- maximum absolute difference `<= 1e-12`.

Duplicate replay is stricter: all stored primary and channel arrays must be
byte-for-byte equal between replicate 1 and replicate 2.

## Primary conditions

The runner reports each preregistered condition separately:

- FULL13 target distance exceeds FULL13 sham distance from INTACT in both
  layouts;
- both subgroup shams exactly reproduce INTACT in both layouts;
- LR subgroup target exactly reproduces FULL13 target in LR;
- RL subgroup target exactly reproduces INTACT in LR;
- RL subgroup target exactly reproduces FULL13 target in RL;
- LR subgroup target exactly reproduces INTACT in RL.

It additionally records one boolean stating whether all preregistered primary
conditions were satisfied. There is no winner.

## Secondary descriptive record

For the three targeted intervention arms, the result records per-DN L2 effect,
DN-channel effect energy, phase-localized effect energy, and the accepted-nine
effect-energy fraction.

These are descriptive outputs only. They do not select new targets.

## Authorization boundary

`--preflight-only` checks identities and the 28-episode plan without executing
neural dynamics.

`--run-frozen` is fail-closed behind a separate tracked authorization artifact.
No authorization artifact is created by this gate.

## Scientific boundary

The SQ-06 groups came from a post-result SQ-05 descriptive audit. A future SQ-06
result can test prospective reproducibility of that frozen observation, but it
does not convert the original observation into independent discovery and does
not rewrite SQ-05.

No biological orientation-circuit, behavior, fear, hunger, threat-perception,
or financial-value claim is authorized.
