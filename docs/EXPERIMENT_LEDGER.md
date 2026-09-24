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

## MQ-5.ER.2 control-selector V1 correction

The first pre-outcome matched-control selector chose edge `3671 -> 27236`.
Although its weight nearly matched `116680 -> 12024`, its structural degrees
were poorly balanced (`pre outdegree 282 vs 4`; `post indegree 104 vs 33`).

No THE RACKET neural outcome had been generated or inspected.

The V1 control candidate was rejected before confirmatory execution. The V2
selector now minimizes the worst log-scale mismatch across weight,
presynaptic outdegree, and postsynaptic indegree before minimizing total
distance.

**Lore:** We brought in a guy who looked right on the books, then discovered he
knew half the city. He was released before questioning.

## MQ-5.ER.2 matched control frozen

THE RACKET matched-control selector V2 selected directed edge:

`78481 -> 16087`

Pre-outcome structural match versus focused edge `116680 -> 12024`:

- same `(3, 3, 3, 3)` hop signature;
- same negative sign;
- presynaptic outdegree `4` versus `4`;
- postsynaptic indegree `37` versus `33`;
- weight `-0.10757946223020554` versus `-0.13293051719665527`.

No THE RACKET neural outcome was generated or inspected during selection.

The V1 candidate `3671 -> 27236` remains rejected as an insufficiently balanced
topology match.

**Lore:** The lineup finally has a civilian. Same neighborhood, similar books,
no one in DETOUR ever named him.

## MQ-5.ER.2 matched-control intervention amendment

Frozen pre-outcome amendment: the structurally matched control
`78481 -> 16087` is now an actual intervention control.

Added arms:

- `CC`: Arm C baseline + matched-control edge lesion.
- `C13C`: original 13-edge lesion + matched-control edge lesion.

The primary focused-edge necessity test remains `C13R` versus `C13`. The
matched-control calibration uses the same endpoint in `C13C` versus `C13`.
Target-set specificity and matched-edge specificity are reported separately.

No MQ-5.ER.2 neural outcome had been generated or inspected before this
amendment.

**Lore:** We have the suspect and we have the civilian. Now both get the same
treatment before anybody starts telling stories.

## MQ-5.ER.2 THE RACKET result

Confirmatory result:

- classification: `RACKET_CAUSAL_SUPPORT_NOT_OBSERVED`
- primary dependency count: `0 / 3`
- matched-control calibration: `NO_PRIMARY_DEPENDENCY_IN_EITHER_INTERVENTION`
- target-set specificity: `SPECIFICITY_NOT_ESTABLISHED`
- result SHA-256: `3c5e18e63330d99c591536a59db9e6d40c5e5e8dca0789b576fa573e6e0bbfb1`
- financial semantics: `NOT ASSIGNED`

All four intervention arms had normalized responder fingerprint distance `0.0`
from their corresponding reference condition.

Post-result integrity audit found both the focused edge `116680 -> 12024` and
matched control `78481 -> 16087` are retina-to-relay edges. Their ordinary
connectome contributions are subject to the frozen retinal double-count-removal
path. This identifies a DETOUR discovery-method issue: pre-cancellation
contribution is not necessarily net effective runtime contribution.

**Lore:** THE RACKET got **Keyser Söze'd**. The focused edge is now **THE
NO-SHOW** — on the books, repeatedly named, and apparently not doing the job
the discovery accounting said he was doing.

## MQ-5.ER.3 RETOUR preregistered

RETOUR is a discovery-only successor to DETOUR and THE RACKET.

It preserves DETOUR's 3-hop dynamic discovery framework but adds a frozen
runtime-alignment gate: ordinary retina-to-relay edges whose connectome
coefficient is exactly mirrored by the frozen relay artifact and subsequently
removed by retinal double-count correction are not eligible candidate edges.

Mandatory negative controls:

- `116680 -> 12024` — THE NO-SHOW
- `78481 -> 16087` — THE RACKET matched control

Both must classify as `DETERMINISTICALLY_CANCELED_RETINA_RELAY` and must be
absent from all RETOUR candidate lists.

Result execution is disabled. Financial semantics remain `NOT ASSIGNED`.

**Lore:** The accountants are going back through the books. Reversed paychecks
do not count as employees anymore.

## MQ-5.ER.3 RETOUR result

RETOUR completed as **DISCOVERY ONLY** with classification
`FOCUSED_RETOUR_CANDIDATES`.

After enforcing the preregistered runtime-alignment rule, `1732` dynamically
eligible retina-to-relay candidate checks were excluded. THE NO-SHOW
`116680 -> 12024` and the matched-control edge `78481 -> 16087` were both
classified `DETERMINISTICALLY_CANCELED_RETINA_RELAY` and were absent from all
candidate lists.

Three runtime-aligned directed edges recurred across at least 3 / 5 affected
targets:

- `11725 -> 29921`
- `11345 -> 47350`
- `10647 -> 51642`

Result SHA-256:
`90d8198a1c218ad24ef29c2c70b4b7a88fd8b24804516d2fd8f20903b847ff3`

No causal claim is authorized. A preregistered intervention is required.

**Lore:** RETOUR followed the package to THE DOCKS. The recurrent candidates
are THE STEVEDORES. Horseface remains a hypothesis; Omar has not appeared.

## MQ-5.ER.4 THE STEVEDORES preregistered

Confirmatory causal follow-up to MQ-5.ER.3 RETOUR.

Frozen candidate edges:

- `11725 -> 29921`
- `11345 -> 47350`
- `10647 -> 51642`

Primary baseline is Arm C + original frozen 13-edge lesion (`C13`).

Planned interventions:

- each candidate lesioned individually on top of C13;
- all three candidates lesioned together on top of C13;
- one outcome-blind structurally matched control per candidate, frozen before
  result execution.

Primary dependency endpoint remains later first-positive onset or target absence.

A descriptive `BUBBLES REPORT` records observable target and waveform changes
without assigning causality or mechanism.

Result execution is disabled. Financial semantics remain `NOT ASSIGNED`.

**Lore:** THE DOCKS had three recurring handlers. THE STEVEDORES asks which one
actually moves Marlo's package, whether the crew covers for each other, and
whether McNulty should have been allowed near the corkboard after midnight.
Horseface remains a theory. Omar has not entered the experiment.


### MQ-5.ER.4 pre-run specificity and stopping-rule audit

Before result execution, the project recorded that RETOUR's focused-recurrence
threshold (`>=3/5` affected targets) was frozen before the discovery run and
that all three STEVEDORE candidates also appeared in at least one retained
comparison target's top-five list. THE STEVEDORES therefore tests necessity and
specificity separately rather than treating discovery recurrence as
affected-set specificity.

A stopping rule is now frozen: null single+combined results close this candidate
set; individual-positive results require a new explicit hypothesis for any
mechanistic follow-up; joint-only results permit one separately preregistered
three-pair follow-up (`S1+S2`, `S1+S3`, `S2+S3`), after which the combination
branch closes absent an independent new hypothesis.


### MQ-5.ER.4 result — THE STEVEDORES

Authoritative artifact SHA-256: `4de3cd6f52782908fc7afad853a5db0e0a1595923de1965c0b47606b5329f5dc`.

S1, S2, and S3 each returned
`SINGLE_EDGE_CAUSAL_SUPPORT_NOT_OBSERVED`; the joint S1+S2+S3 lesion returned
`COMBINED_SET_CAUSAL_SUPPORT_NOT_OBSERVED` with `0/5` affected-target
dependencies. No redundancy-compatible pattern was observed.

S3 did alter secondary positive-voltage amplitude for a subset of responders
without changing first-positive onset. That observation remains descriptive
only and does not upgrade the frozen causal endpoint.

The STEVEDORES candidate branch closes here under the precommitted stopping
rule. Any further work must begin from a new independent hypothesis.


### MQ-5.ER.5 preregistration — THE GREEK

THE STEVEDORES branch is closed under its frozen stopping rule. THE GREEK opens
a new discovery question rather than searching for replacement stevedores:
whether C13 onset timing is preserved by a shared upstream or parallel routing
structure that reaches multiple affected responders before their frozen
onsets.

The discovery searches coordinator **nodes**, not replacement edges, within
three reverse hops. Ranking, retained-target reporting, top-5 limit, and branch
closure rules are frozen before result execution. No causal intervention is
authorized by MQ-5.ER.5 itself.

Financial semantics remain `NOT ASSIGNED`.

### MQ-5.ER.5 result — THE GREEK

Authoritative result status: **SEALED / COMPLETED**

Classification:

`GREEK_FOCUSED_COORDINATOR_CANDIDATE`

The frozen discovery rule found a focused upstream coordinator candidate.
Node `1952` ranked first and covered all five affected responders, while also
covering all four retained comparison responders. The complete deterministic
top five was:

`1952, 2641, 1963, 1944, 23640`

All five covered `5/5` affected and `4/4` retained targets.

This result supports the preregistered discovery conclusion that a focused
coordinator candidate exists under the frozen three-hop search and timing rule.
It does not establish unique control or causal necessity/sufficiency.

Eligible candidate count: `17340`

Authoritative result SHA-256:

`1ed37ae6d4e19cd39409a2bb714ed7394236d2a273316005c6ae596e5d837790`

Result seal SHA-256:

`63fb631e661ff054e28869f0c784eddea088ab8c3307a0c82bc5d55a40b94ee9`

Frozen scientific execution SHA:

`4978062b48b557ad9f8f327308ce4aeca0a49ae3`

Per the preregistered stopping rule, any candidate intervention must be a new,
separately preregistered causal experiment with matched controls.

Financial semantics remain `NOT ASSIGNED`.

## SQ-05 — TWO BETRAYALS — sealed result

SQ-05 completed as a preregistered, local authoritative result using the frozen
192-frame dual-cue visual sequence, the inherited 13-edge causal-route lesion,
its frozen matched sham, and the frozen 20-seed strict matched-topology null.

Authoritative result status: **SEALED / COMPLETED**

Primary result components:

- Cue B produced a measured model response in both frozen retinal layouts.
- The inherited 13-edge targeted lesion exceeded the matched sham in both
  layouts.
- The strict matched-topology null reproduced the intact response in `0 / 20`
  seeds.
- All six deterministic arm/layout duplicate pairs replayed exactly.
- No single overall winner is defined.

Frozen lesion-versus-intact normalized symmetric L2 distance:

- `LR`: `3.8240768866345015e-05`
- `RL`: `0.1276743202466753`

Authoritative result SHA-256:

`72bbef6b8cd996f81a371938af9fd3f024ef381bce8cf458c378dc55b05646b1`

Authoritative sidecar SHA-256:

`b3fbe9f28d07aa5d8dfe707eed99e4b7b48b28364e1afc37875e8442fbeb7a8e`

Result seal SHA-256:

`fbd902de5ddae4913af337e3d9a1a77ed55750edfe808a6863d8fb24c949f48a`

Seal commit:

`2146c9f4e6f929985a92c9787ef3e018b127c14a`

The lesion predates SQ-05 and retains its historical `post_hoc = true`
discovery provenance from MQ-3.2. SQ-05 prospectively adopted the already-fixed
lesion; it did not prospectively discover those 13 edges.

SQ-05 supports model/network-response claims only. It does not establish fruit
recognition, hunger, threat perception, fear, behavior, biological causality,
population-level significance, market prediction, or financial value.

## SQ-06 — SILENT CARTOGRAPHER — sealed result

SQ-06 prospectively tested an orientation grouping that had been observed only
after the sealed SQ-05 result. The grouping was frozen before SQ-06 execution:

- `LR_OBSERVED`: 10 of the historical 13 targeted edges;
- `RL_OBSERVED`: the remaining 3 targeted edges.

Authoritative result status: **SEALED / COMPLETED**

All six preregistered primary conditions were satisfied:

- `FULL13_TARGETED` exceeded `FULL13_SHAM` relative to intact in both layouts;
- `LR_GROUP_SHAM` and `RL_GROUP_SHAM` exactly reproduced intact in both layouts;
- in `LR`, `LR_GROUP_TARGETED` exactly reproduced `FULL13_TARGETED`;
- in `LR`, `RL_GROUP_TARGETED` exactly reproduced `INTACT`;
- in `RL`, `RL_GROUP_TARGETED` exactly reproduced `FULL13_TARGETED`;
- in `RL`, `LR_GROUP_TARGETED` exactly reproduced `INTACT`.

Execution completed `28 / 28` episodes with `14 / 14` exact duplicate
arm/layout pairs. The stored DN spike count across all 28 episodes was `0`; the
primary endpoint was subthreshold positive membrane voltage.

The exact partition result is **prospective validation of an SQ-05-derived
grouping**. It is not independent discovery and does not establish a biological
orientation circuit or behavior.

Authoritative result SHA-256:

`f9fe6e3ea23edc86869e7e47fa88ab11c25a607b8fe4fce6b5cdec2c8c0a58a9`

Authoritative sidecar SHA-256:

`f10b9769bd799a390295ced25b99c2a98e3efe49c823c2a5a79595d28fcc0feb`

Result seal SHA-256:

`de7129a812a4520706512234be19543a51df64fa9879f50bee8d8a2045b5b816`

Seal commit:

`ba16e60ca798997ad1b1a7a9f06322f3679abe14`

No minimum meaningful-effect floor was defined, no post-result threshold is
introduced here, and no single overall winner is defined.
