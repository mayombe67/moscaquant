# MoscaQuant Experiment Ledger

This ledger is the durable chronological record of scientific experiments,
engineering pilots, verification runs, and result-bearing executions.

It answers a different question from the Highlight Reel:

- **Highlight Reel:** what was especially interesting?
- **Experiment Ledger:** what did we actually run, under what status, and what
  is authoritative?

## Status vocabulary

- `PREREGISTERED` — protocol frozen; no result yet.
- `VERIFICATION` — checks already-known facts or implementation neutrality.
- `ENGINEERING PILOT` — non-authoritative feasibility/performance run.
- `DISCOVERY` — result may generate hypotheses but cannot confirm them.
- `CONFIRMATORY` — prospectively frozen causal/replication test.
- `COMPLETE` — documented and closed.

## Authority rules

1. Engineering pilots cannot replace, shrink, or amend a frozen scientific
   experiment.
2. Pilot outcomes cannot select thresholds, candidate rules, or confirmatory
   interventions for the authoritative experiment unless that use was itself
   preregistered before the pilot.
3. Superseded or failed runs remain in the ledger.
4. Result artifacts record SHA-256 where available.
5. Git commits are recorded only when known; missing historical commit IDs are
   left explicitly unknown rather than reconstructed from memory.
6. Financial semantics remain `NOT ASSIGNED` unless explicitly changed by a
   separate scientific decision.

## Current ledger

| ID | Codename / purpose | Kind | Status | Authoritative? | Result / note | Artifact / SHA | Git |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MQ-5.TS | Topology specificity | Confirmatory | COMPLETE | Yes | Specific wiring arrangement supported under frozen tested nulls | `mq5-ts-topology-specificity-v1.json` / `903bff56fba99580b93db2a875f4c1996e3976a018bb26d306ef61baf73b2811` | closeout `48536a7` |
| MQ-5.ER | Encoding robustness | Confirmatory | COMPLETE | Yes | Selective encoding robustness; Arm C altered causal dependency | `mq5-er-encoding-robustness-v1.json` / `737a316a98d91b95dc1a5fe3ac25e7bf229447ae422ecd23ecf39ea8d4f6bb39` | historical closeout commit: not recorded here yet |
| MQ-5.ER.1 | DETOUR | Discovery | COMPLETE | Yes | `FOCUSED_DETOUR_CANDIDATES`; focused edge `116680 -> 12024`; ROADBLOCK required | `mq5-er1-detour-v1.json` / `4b06c0181514f01715319dfacfa91569202067e583db7ef9fda5f35818eb4611` | closeout `faa29a6` |
| MQ-5.ER.1-VR1 | DETOUR known-parent replay | Verification | COMPLETE | No | Arm A/C stimulus hashes and onset vectors exactly reproduced; no candidate scoring | none | `6efa04f24b0db1120975829756d25f5189d716a0` |
| MQ-5.ER.1-LP | DETOUR laptop pilot R1 | Engineering pilot | COMPLETE | No | `DIFFUSE_DETOUR_CANDIDATES`; two-hop non-authoritative pilot; cannot supply ROADBLOCK candidates | `mq5-er1-detour-laptop-pilot-v1.json` / `a1f1e6f5cffc707253479298dc8a44cc902b005b23f2d8805304ce84b22cad0f` | result HEAD `68e5067` |
| MQ-5.ER.1-LP-R2 | DETOUR laptop pilot R2 | Engineering pilot | COMPLETE | No | Hardened-scorer replication; reproduced R1 classification/candidate ordering | `mq5-er1-detour-laptop-pilot-r2-v1.json` / `fe854e49f85ec8f4e54828bc96413d7333003d0b64a294e815efe6804e143aaa` | result HEAD `fa2af08` |

## MQ-5.ER.1-VR1 verification details

The known-parent replay completed successfully before any DETOUR result
authorization.

Verified Arm-A stimulus SHA-256:

`9c06a18293dd7dd27b1a1717785e2da25518d4b0081e5266794c3166a3f471e9`

Verified Arm-C stimulus SHA-256:

`e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a`

Replay Git HEAD:

`6efa04f24b0db1120975829756d25f5189d716a0`

Observed engineering performance:

- elapsed wall time: approximately 18.11 seconds;
- maximum resident set: approximately 2.35 GiB;
- swap: 0;
- result execution: false;
- status: `KNOWN-REPLAY-VERIFIED`.

The replay exposed no new DETOUR candidate result.

## Backfill policy

Older MoscaQuant experiments should be added from repository artifacts,
protocols, commits, and result files rather than from memory alone.

Backfill is documentation work only and must not reinterpret historical
scientific classifications.

## Lore notes

Lore remains downstream of the evidence. These notes are presentation canon
only and do not modify status, authority, classification, or claim boundaries.

- **MQ-5.TS — Office Gossip:** Management shuffled the org chart twenty times.
  Morty still knew exactly which wiring diagram was the real one.
- **MQ-5.ER — Office Gossip:** Management moved the desks, changed the meeting
  cadence, and killed the animations. Morty kept working. They removed temporal
  chaos and five departments quietly stopped using the approved chain of
  command.
- **MQ-5.ER.1 — DETOUR:** The three-hop neighborhood turned out to be most of
  the city.
- **MQ-5.ER.1-VR1 — Surveillance Log:** The wiretap reproduced the known
  timeline exactly. Morty did not notice the surveillance equipment.
- **MQ-5.ER.1-LP — Jurisdiction Notice:** Local law enforcement is authorized
  for two hops only. Federal agents will handle hop three.
- **Engineering incident:** The first DETOUR inventory attempt caused the
  surveillance laptop to flee the scene. No scientific result was generated.

## MQ-5.ER.1-LP implementation note

The laptop-pilot wrapper reuses the authoritative DETOUR factorized scorer with
an explicit two-hop parameter. The authoritative runner's default remains
three hops. Pilot execution remains disabled pending a separate authorization
checkpoint.

## DETOUR scorer hardening

Before authoritative 3-hop DETOUR execution, the streaming scorer was hardened
so exact-score ties cannot be arbitrarily reduced by `numpy.argpartition`.
The frozen score and ranking rules are unchanged.

**Lore:** Witnesses with identical stories are now lined up by badge number
instead of whichever five happen to get shoved into the squad car first.

## DETOUR known-replay lesion verification

The DETOUR replay gate now checks the frozen C-LESION13 onset vector as well as
Arm A and Arm C baseline replay.

This is verification of already-known parent-experiment behavior, not a new
DETOUR result.

**Lore:** Internal Affairs now checks the getaway car too, not just the
suspects standing in the lineup.

## MQ-5.ER.1-LP-R2 — hardened-scorer replication

A second two-hop laptop pilot is authorized only as an engineering replication
after deterministic tie-handling hardening and C-LESION13 replay verification.

R2 uses the same two-hop scope and the same non-authoritative claim boundary as
R1. Its purpose is to compare candidate ordering and pilot classification
against R1 under the hardened implementation.

R2 cannot supply MQ-5.ER.2 ROADBLOCK candidates.

**Lore:** Same neighborhood, same warrant, better paperwork.

## MQ-5.ER.1 3-hop synthetic stress benchmark

Before deciding whether to run the frozen authoritative 3-hop DETOUR locally,
a non-result engineering benchmark may exercise the same streaming scorer at
three hops using synthetic all-ones activity summaries.

The benchmark:

- uses the real connectome topology and frozen lesion-edge set;
- uses the same 3-hop streaming traversal/scoring code path;
- does **not** use Arm A, Arm C, or C-LESION13 dynamic activity;
- emits no candidate identities;
- cannot produce or alter a DETOUR scientific classification.

Its only purpose is to estimate local runtime/compute cost.

**Lore:** Federal agents are walking the route with rubber evidence bags before
the real raid.

## MQ-5.ER.1 — DETOUR authoritative result

MQ-5.ER.1 completed under the frozen 3-hop protocol.

- Classification: `FOCUSED_DETOUR_CANDIDATES`
- Artifact SHA-256: `4b06c0181514f01715319dfacfa91569202067e583db7ef9fda5f35818eb4611`
- Result Git HEAD: `04c24ef3396a0f6461504308592cbe6538d0dfb3`
- Focused recurring edge: `116680 -> 12024`
- Affected targets containing that edge: 92, 656, 137122
- Retained comparison target also containing that edge: 1273
- Required follow-up: MQ-5.ER.2 ROADBLOCK
- Causal claims: not authorized
- Financial semantics: NOT ASSIGNED

**Lore:** Federal agents finally got three affected witnesses to name the same
guy. Then 1273 walked in and said, "Yeah, I know him too."

## MQ-5.ER.2 — THE RACKET preregistration

THE RACKET is the prospective confirmatory follow-up to DETOUR.

- focused edge: `116680 -> 12024`
- primary targets: `92`, `656`, `137122`
- key retained comparison: `1273`
- primary causal comparison: C13R versus C13
- result execution: disabled
- financial semantics: NOT ASSIGNED
- prior placeholder codename: ROADBLOCK

**Lore:** DETOUR found the guy everybody named. THE RACKET finds out whether
he actually runs the operation — or whether somebody put him out front to take
the heat.
