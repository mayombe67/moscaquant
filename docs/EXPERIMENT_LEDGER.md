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
| MQ-5.ER.1 | DETOUR | Discovery | PREREGISTERED | Yes when executed under frozen 3-hop protocol | Full result deferred pending suitable execution environment | none | streaming runner checkpoint `6efa04f24b0db1120975829756d25f5189d716a0` |
| MQ-5.ER.1-VR1 | DETOUR known-parent replay | Verification | COMPLETE | No | Arm A/C stimulus hashes and onset vectors exactly reproduced; no candidate scoring | none | `6efa04f24b0db1120975829756d25f5189d716a0` |
| MQ-5.ER.1-LP | DETOUR laptop pilot | Engineering pilot | PREREGISTERED | No | Two-hop feasibility run only; cannot supply ROADBLOCK candidates | pilot artifact not yet produced | pending |

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
