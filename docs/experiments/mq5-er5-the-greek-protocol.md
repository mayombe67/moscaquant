# MQ-5.ER.5 — THE GREEK

Status: **PREREGISTERED DISCOVERY — RESULT EXECUTION DISABLED**

Financial semantics: `NOT ASSIGNED`

Parent result:
- MQ-5.ER.4 — THE STEVEDORES
- SHA-256: `4de3cd6f52782908fc7afad853a5db0e0a1595923de1965c0b47606b5329f5dc`

## Why this experiment exists

THE STEVEDORES closed the three-edge confirmatory branch cleanly. S1, S2, and
S3 were not necessary for first-positive onset individually, and the joint
S1+S2+S3 lesion was also null on the frozen onset-dependency endpoint.

The new hypothesis is therefore not "find a better stevedore."

The new hypothesis is:

> C13 onset timing may be preserved by a shared upstream or parallel routing
> structure that reaches multiple affected responders before their frozen
> first-positive onsets.

THE GREEK is a discovery experiment for that hypothesis. "The Greek" is a lore
name for an unidentified coordinating or common-source mechanism. It is **not**
a neuron identity, biological claim, or causal conclusion.

## Frozen state

Condition: `C13` — Arm C with the original frozen 13-edge lesion.

Frames: `192`

Arm-C stimulus SHA-256:
`e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a`

Frozen C13 first-positive onsets:

- `51 -> 150`
- `55 -> 145`
- `92 -> 141`
- `129 -> 149`
- `317 -> 156`
- `656 -> 141`
- `1273 -> 149`
- `126002 -> 151`
- `137122 -> 151`

Affected targets:
`55, 92, 656, 126002, 137122`

Retained comparison targets:
`51, 129, 317, 1273`

## Discovery object

THE GREEK searches for **upstream coordinator candidates**, not replacement
edges.

A coordinator candidate is a node that satisfies all frozen eligibility rules:

1. it is a reverse ancestor of at least one frozen affected target;
2. shortest directed distance to that target is at most `3` edges;
3. it is not itself one of the nine frozen responder targets;
4. it is not an edge-level candidate from RETOUR/STEVEDORES being recycled under
   a new name;
5. its runtime activity becomes positive before the frozen onset of each
   affected target counted in its coverage;
6. ancestry traversal may pass through runtime-special interfaces, but any
   candidate-level dynamic score must use the same runtime-aligned exclusions
   that RETOUR introduced after THE RACKET.

## Frozen primary discovery quantities

For every eligible node, compute:

- `affected_coverage`: number of the 5 affected targets reachable within 3 hops
  for which the node also satisfies the pre-onset activity rule;
- `retained_coverage`: number of the 4 retained targets satisfying the same
  rule;
- exact shortest-hop signature to each covered target;
- first-positive activity frame of the candidate node;
- minimum lead in frames relative to each covered target onset;
- integrated positive candidate activity through the latest covered affected
  target onset;
- number of distinct immediate downstream branches from the candidate that
  participate in shortest paths to covered affected targets.

No single quantity is a causal effect.

## Frozen ranking

Candidates are ranked deterministically by:

1. higher `affected_coverage`;
2. higher number of distinct downstream branches participating in affected
   shortest paths;
3. larger minimum temporal lead across covered affected targets;
4. lower `retained_coverage`;
5. lower maximum shortest-hop distance to covered affected targets;
6. lower node id.

No ranking field may be changed after discovery output is inspected.

## Frozen classification

`GREEK_FOCUSED_COORDINATOR_CANDIDATE`
- at least one eligible node has `affected_coverage >= 4`.

`GREEK_DISTRIBUTED_COORDINATOR_PATTERN`
- eligible candidates exist, but no single node reaches 4/5 affected targets;
- at least two candidates together cover all 5 affected targets.

`NO_CLEAR_GREEK_COORDINATOR`
- neither condition above is met.

The classification is discovery-only.

## Specificity reporting

Retained-target coverage is always reported.

A candidate is **not** called affected-set-specific merely because it ranks
highly. If it also covers retained targets, that fact is carried forward
explicitly.

## No-free-looks rule

THE GREEK may emit at most the deterministic top `5` coordinator candidates.

No candidate intervention is authorized by this experiment.

If a focused or distributed coordinator pattern is observed, any causal test
must be a new separately preregistered experiment with frozen interventions and
matched controls.

If `NO_CLEAR_GREEK_COORDINATOR` is observed, this upstream-coordinator branch
closes. No threshold lowering, hop-depth expansion, or top-k expansion is
authorized from the same result.

## Claim limits

THE GREEK does not authorize claims of:

- biological identity;
- cognition or intent;
- market understanding;
- financial meaning;
- trading or predictive value;
- causal necessity or sufficiency;
- unique control;
- "The Greek" being a literal single node.

## Lore / command presence

The scientific question is straightforward: the shipment kept arriving after
the three stevedores were removed, so the investigation moves upstream without
reopening the closed dockworker case.

Cedric Daniels is now the command-presence character. He intervenes whenever
McNulty tries to turn a discovery pattern into a causal conclusion or tries to
move a frozen threshold after seeing a result.

The Destiny bleed-through is intentionally progressive and remains lore-only.
As protocol discipline accumulates, Daniels' language gradually takes on
Commander Zavala cadence and references. The team understands both narratives:
Daniels is still running the Baltimore unit, but the more rigorously the unit
follows protocol, the more he sounds like he has also been commanding the
Vanguard for several centuries.

Current command-presence state: **DANIELS / ZAVALA BLEED 5%**

Daniels, looking at the closed STEVEDORES board:

> "Whether we wanted it or not, we've stepped into a war with hidden routing
> redundancy."

McNulty: "That's not how you usually talk."

Daniels: "Neither is moving a preregistered threshold after the fact."

Lester understands exactly what he means.

Bubbles is off-duty from the experiment until descriptive street-level
telemetry is needed again.
