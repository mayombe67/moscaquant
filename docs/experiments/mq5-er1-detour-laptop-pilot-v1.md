# MQ-5.ER.1-LP — DETOUR Laptop Pilot

**Status:** PREREGISTERED ENGINEERING PILOT

**Authority:** NON-AUTHORITATIVE

**Parent scientific experiment:** MQ-5.ER.1 — DETOUR

**Financial semantics:** NOT ASSIGNED

## Purpose

The laptop pilot exists only to validate the factorized DETOUR execution path
on current local hardware before the authoritative frozen 3-hop DETOUR run is
moved to a suitable spot-instance/cloud execution profile.

It is intentionally smaller than the scientific experiment.

## Frozen pilot difference

The only scientific-scope reduction relative to MQ-5.ER.1 is:

- maximum backward search depth: **2 hops instead of 3**.

Everything else should reuse the already-frozen DETOUR machinery where
applicable:

- A-BASELINE;
- C-BASELINE;
- C-LESION13;
- same affected targets;
- same retained-dependency comparison targets;
- same parent onset windows;
- same candidate score;
- same top-5 cap;
- same deterministic tie order.

## Prohibited uses

The laptop pilot SHALL NOT:

- replace the authoritative 3-hop DETOUR result;
- amend the 3-hop preregistration;
- supply candidates to MQ-5.ER.2 ROADBLOCK;
- tune the candidate score;
- change candidate thresholds;
- change the top-K cap;
- justify dropping a target;
- justify a narrower authoritative search depth;
- create causal claims.

ROADBLOCK candidates may come only from the eventual full frozen 3-hop DETOUR.

## Allowed outputs

The pilot may report:

- runtime;
- peak-memory behavior;
- whether the factorized scorer completes;
- two-hop discovery candidates;
- the two-hop discovery family label.

Any candidate/classification must be visibly marked:

`ENGINEERING PILOT — NON-AUTHORITATIVE`

## Interpretation boundary

A two-hop candidate may be scientifically interesting, but its presence or
absence is not a result of the preregistered MQ-5.ER.1 DETOUR experiment.

The authoritative scientific question remains deferred until the frozen 3-hop
run is executed unchanged.
