# MOSCAQUANT PROJECT CHARTER

**Document:** MQ-CHARTER-002
**Owner:** YOLO & HODL LLC
**Subject:** MQ-001
**Status:** ACTIVE
**Classification:** CONNECTOMIC / FINANCIAL
**Revision:** 2.0
**Date:** September 2026

> **THE MARKET PROVIDES FEEDBACK.
> WE PROVIDE CONSEQUENCES.**

**166,700 neurons. Zero fiduciary responsibility.**

---

## 1. Mission

MoscaQuant is an experimental autonomous market agent built around the
complete adult male *Drosophila melanogaster* CNS connectome.

The project investigates whether biological neural topology can serve as the
computational substrate of an autonomous financial agent and whether market
stimuli can produce reproducible, behaviorally meaningful neural responses.

MoscaQuant is not a conventional trading algorithm decorated with a fruit-fly
theme.

The connectome is the decision substrate.

**The Mosca makes the decision. The Warden controls the money.**

---

## 2. Subject

**Designation:** MQ-001
**Corporate designation:** Employee #0001
**Species:** *Drosophila melanogaster*
**Organization:** YOLO & HODL LLC
**Division:** Quantitative Strategies

MQ-001 is derived from the complete adult male CNS connectome containing
approximately 166,700 neurons.

The biological connectome provides structural topology.

Neural dynamics, market-to-sensory mappings, financial decision mappings,
plasticity rules, and embodiment are modeled components and must never be
misrepresented as biologically complete simulations.

---

## 3. Prime Experimental Questions

MoscaQuant exists to investigate:

1. Does biological connectome topology matter?
2. Does MQ-001 behave differently from a topology-preserving randomized control?
3. Do market stimuli generate reproducible neural states?
4. Can neural states predict subsequent market behavior?
5. Can useful financial decisions emerge from those states?
6. Does aversive intervention alter future behavior?
7. Does learned behavior persist?
8. Do different corrective interventions produce measurably different outcomes?
9. Does apparent performance survive out-of-sample testing?
10. Is the entire experiment merely an extraordinarily elaborate coin flip?

Negative results are valid results.

A modeled mechanism rejected by a precommitted experimental gate remains part
of the permanent record. It must not be silently retuned against withheld
market conditions until it produces a desired downstream response.

---

## 4. Authorized Market Universe

The intended initial trading universe is:

- BTC
- ETH
- SOL
- XRP
- HBAR
- DOGE

Availability remains subject to supported broker APIs and WARDEN-01 controls.

The universe may eventually expand through an explicit architecture decision.

MQ-001 does not control the authorized universe.

---

## 5. System Architecture

```text
LIVE CRYPTO MARKET
        ↓
MARKET FEATURE ENCODER
        ↓
ARTIFICIAL SENSORY STIMULATION
        ↓
MQ-001 / MALE CNS CONNECTOME
        ↓
NEURAL ACTIVITY
        ↓
BEHAVIORAL READOUT
        ↓
BUY / HOLD / SELL
        ↓
TRADE PROPOSAL
        ↓
WARDEN-01
        ↓
BROKER
        ↓
PROFIT / DISGRACE

The neural agent proposes financial behavior.

The risk system independently decides whether that behavior may reach the
outside world.

The brain proposes. The Pi disposes.

6. The Habitat

The Habitat executes the connectome simulation and associated experimental
systems.

Habitat v1

Initial development hardware:

Samsung Galaxy Book Pro
Intel Core i5-1135G7
4 cores / 8 threads
7.4 GiB usable RAM
4 GiB swap
Intel Iris Xe
NVMe storage
Ubuntu Linux
Python 3.12
Docker

Habitat v1 is a development environment, not a permanent architectural
dependency.

Because memory is constrained:

connectivity must remain sparse;
dense whole-connectome adjacency matrices are prohibited;
compact numeric representations should be used where scientifically valid;
large structures may be memory-mapped;
preprocessing may be chunked;
telemetry should be streamed rather than retained indefinitely in RAM.

Optimization occurs before hardware replacement.

7. Cloud Portability

MoscaQuant shall be cloud-portable from the beginning.

Components must not depend unnecessarily upon Habitat-specific paths, devices,
credentials, or configuration.

Development may begin locally while heavy computation migrates incrementally
to cloud infrastructure.

The intended progression is:

LOCAL DEVELOPMENT
        ↓
HYBRID LOCAL / CLOUD
        ↓
CLOUD COMPUTE
        ↓
CLOUD TELEMETRY + STORAGE
        ↓
CLOUD PANOPTICON
        ↓
PREDOMINANTLY CLOUD-RESIDENT MOSCAQUANT

Containerization should favor simple, portable deployment.

Docker Compose is preferred initially.

Kubernetes will not be introduced merely because management has heard of it.

8. WARDEN-01

WARDEN-01 is the independent risk and authorization authority.

Initial physical host:

Raspberry Pi 3

Responsibilities include:

broker authentication;
order validation;
position validation;
asset allowlisting;
maximum position limits;
total exposure limits;
daily loss limits;
order-frequency limits;
cooldown enforcement;
stale-data detection;
duplicate-order detection;
watchdog operation;
emergency shutdown;
execution logging;
Sugar Cube Protocol enforcement.

MQ-001 shall never possess broker credentials.

MQ-001 shall never modify Warden risk policy.

Failure of communication between Habitat and Warden defaults to:

DENY.

If WARDEN-01 eventually migrates to cloud infrastructure, it must remain
logically and operationally isolated from MQ-001.

9. Sugar Cube Protocol

Sugar Cube Mode is the hard containment state for financial activity.

Possible triggers include:

daily loss limit reached;
stale market feed;
Habitat failure;
Warden failure;
broker/account mismatch;
abnormal order frequency;
malformed proposal;
impossible neural output;
unauthorized asset;
manual kill switch.

When activated:

SUGAR_CUBE_MODE = TRUE

New trades are denied.

Existing positions follow predefined Warden policy.

MQ-001 cannot disable Sugar Cube Mode.

The Oracle cannot disable Sugar Cube Mode.

Mercy cannot disable Sugar Cube Mode.

10. The Oracle

The Oracle implements the D6 Behavioral Correction Protocol.

When designated experimental loss conditions occur:

Sugar Cube Mode activates.
Financial activity stops.
A cryptographically unbiased D6 is rolled.
The corresponding experimental intervention is applied.
D6 Protocol

1 — THE SHOCK

Strong artificial aversive stimulation is delivered to designated populations.

2 — DARKNESS

Market sensory input is heavily attenuated during a defined deprivation period.

3 — BAD SYNAPSE

When plasticity experiments are active, pathways associated with recent losing
behavior receive an experimental negative update.

4 — TIME OUT

Trading-output populations are inhibited for the defined experimental period.

5 — SCAR TISSUE

A persistent aversive state survives into the following experimental session.

6 — MERCY

No aversive intervention occurs. A limited positive neuromodulatory event may
be introduced.

Mercy does not reopen trading.

The Oracle modifies the simulated subject only.

It never modifies Warden policy.

Failure is permitted. Repetition is corrected.

11. Learning and Plasticity

Structural connectivity does not itself imply learning.

Persistent behavioral modification requires explicitly implemented and
versioned plasticity or state mechanisms.

Experiments must distinguish:

frozen-connectome behavior;
plastic connectome behavior;
punished behavior;
unpunished controls;
persistent state;
transient stimulation.

Every plasticity assumption must be documented.

12. Experimental Controls

Canonical controls include:

MOSCA

Real MaleCNS topology.

SHUFFLED MOSCA

Randomized topology preserving relevant statistical characteristics where
possible.

DEAD MOSCA

Simple conventional model.

MOMENTUM CHIMP

Basic momentum strategy.

COIN-FLIP PORTFOLIO MANAGER

Random financial decisions.

BUY & HOLD

Passive market baseline.

The most important structural comparison is:

MOSCA vs SHUFFLED MOSCA

If a control wins, the result will be reported.

Management disappointment does not constitute statistical significance.

13. MQ-001 Embodiment

MQ-001 will eventually inhabit a virtual 3D body inside a simulated containment
chamber and trading workstation.

The subject is visually restrained to the trading station.

This is both thematic and architectural: MQ-001 has agency within the
experiment but no unrestricted authority over the external financial system.

Where biologically meaningful mappings are available, virtual body behavior
should derive from actual neural and motor telemetry rather than canned
BUY/SELL animations.

Potential observable behaviors include:

approach;
retreat;
orientation;
locomotion;
startle;
grooming;
wing activity;
conflicting motor activity.

The embodiment must remain explicitly distinct from claims of a complete
biomechanical fly simulation.

14. The Containment Chamber

The Containment Chamber is the primary spectator representation of MQ-001.

Its visual direction intentionally resembles a late-1990s/early-2000s
scientific or containment simulator.

The PS1/PS2-inspired environment is an artistic choice rather than a technical
limitation.

The chamber may contain:

MQ-001;
trading workstation;
physical restraint metaphor;
market displays;
surveillance cameras;
containment indicators;
Oracle equipment;
sugar-cube dispenser;
environmental lighting;
corporate messaging.

Oracle events should visibly affect the environment and subject.

15. Neuroscope

Neuroscope is the detailed scientific visualization of MQ-001.

It should visualize real simulator telemetry rather than decorative neural
activity.

Capabilities may include:

actual neuron positions;
live activity;
population activity;
selected connectivity;
signal propagation;
sensory pathways;
financial output populations;
Oracle effects;
neural metadata;
replay.

Rendering all connections continuously is neither required nor desirable.

Neuroscope should prioritize active, strong, selected, or experimentally
relevant pathways.

The spectator interface should eventually permit a transition from the
Containment Chamber into Neuroscope, visually moving from the embodied subject
into its nervous system.

16. The Panopticon

The Panopticon is MoscaQuant's public observational interface.

It may eventually expose:

Containment Chamber;
Neuroscope;
market state;
MQ-001 decisions;
confidence;
trade proposals;
Warden decisions;
executions;
P/L;
Sugar Cube status;
Oracle events;
achievements;
personnel records;
experiment methodology;
benchmark results;
incident reports;
historical replay.

The public interface must distinguish:

NEURAL DECISION
      ↓
TRADE PROPOSAL
      ↓
RISK DECISION
      ↓
BROKER EXECUTION

This separation demonstrates that WARDEN-01 is not secretly implementing the
trading strategy.

Secrets, credentials, private keys, and sensitive infrastructure data must
never enter public telemetry.

17. Interpretation Layer

Human-readable descriptions of MQ-001 neural states are entertainment and
observability aids.

For example:

ACTUAL TELEMETRY

THREAT ACTIVITY: ELEVATED
APPROACH: 74%
VOLATILITY STIMULUS: HIGH

may become:

MQ-001 INTERPRETATION

"THE LARGE RED THING CANNOT HURT ME."

Such output must be identified as automated interpretation.

It is not literal thought reading.

18. Telemetry and Replay

MoscaQuant is event-driven and should retain sufficient information to
reproduce important experimental decisions.

Core events include:

MARKET_STATE
FEATURE_VECTOR
SENSORY_STIMULUS
NEURAL_ACTIVITY
NEURAL_SPIKE
POPULATION_ACTIVITY
TRADE_DECISION
ORDER_PROPOSAL
RISK_DECISION
ORDER_EXECUTED
POSITION_UPDATE
LOSS_LIMIT
SUGAR_CUBE
DICE_ROLL
CORRECTIVE_ACTION
PLASTICITY_UPDATE
ACHIEVEMENT
INCIDENT
SESSION_END

Events must include appropriate timestamps and identifiers.

Replay should eventually reconstruct:

MARKET
   ↓
STIMULUS
   ↓
NEURAL PROPAGATION
   ↓
DECISION
   ↓
WARDEN
   ↓
EXECUTION
   ↓
OUTCOME
19. Achievements

Achievements are permanent experimental metadata and public satire.

Canonical achievements include:

BUY HIGH, SELL LOW
LEARN NOTHING
THE MARKET TAUGHT ME
GOD'S FAVORITE IDIOT
DIAMOND ANTENNAE
REGARDED BY NATURE
HOUSE ALWAYS WINS
PTSD MODE
CRAMER MODE
TOO DUMB TO FAIL
HE'S BEGINNING TO BELIEVE
PAVLOV WOULD BE PROUD
THIS SHOULD NOT BE WORKING
ACTUALLY SENTIENT?
I HAVE NO MOUTH AND I MUST TRADE
TENURE
0DTE REQUEST DENIED
DELETE THE REPOSITORY

Achievements confer no financial authority.

20. Corporate Structure

MQ-001 may progress through the fictional corporate ladder:

INTERN
JUNIOR QUANT
QUANT
SENIOR QUANT
PORTFOLIO MANAGER
MANAGING DIRECTOR
APEX INSECT

Promotions confer prestige only.

They never modify Warden limits.

Corporate satire may include:

performance reviews;
Performance Improvement Plans;
administrative leave;
appeals;
morale;
propaganda;
compliance training;
investor relations;
quarterly reports.

Appeals may exist for employee morale.

They need not succeed.

21. Documentation Tone

MoscaQuant uses a deliberate hierarchy of themes.

Brand

MoscaQuant / YOLO & HODL LLC.

Financial culture

WallStreetBets-inspired absurdity, benchmarks, achievements and financial
degeneracy.

Tone

Corporate dystopia and Black Mirror-style bureaucracy.

Documentation

Original anomalous-containment language inspired by clinical containment
fiction.

MoscaQuant does not claim affiliation with any external fictional universe.

As MQ-001 behavior becomes more scientifically interesting or unexpected,
official documentation should become less comedic and more clinical.

22. Scientific Integrity

MoscaQuant will clearly distinguish:

Known biological structure

from

modeled neural dynamics

from

artificial market interfaces

from

entertainment presentation.

Claims of intelligence, learning, sentience, biological realism, or financial
performance require evidence appropriate to the claim.

Tiny profitable samples are not alpha.

Interesting behavior is not sentience.

A connectome is not a complete organism.

The joke does not override the experiment.

23. Real-Money Execution

The intended endpoint includes controlled real-money cryptocurrency execution.

Initial execution shall be extremely limited.

Broker integration progresses through:

NO BROKER
   ↓
READ ONLY
   ↓
ACCOUNT RECONCILIATION
   ↓
ORDER VALIDATION
   ↓
TINY LIVE ORDERS
   ↓
CONTROLLED LIVE OPERATION

No broker credentials enter MQ-001.

No leverage is granted merely to increase entertainment value.

Options are outside the authorized system.

24. Roadmap
MQ-0 — ACQUIRE SUBJECT

Load and validate the MaleCNS dataset.

Generate sparse representation.

Identify initial populations.

Deliver controlled stimulus.

Observe and record propagation.

MQ-1 — IT'S ALIVE

Implement reproducible neural dynamics.

MQ-2 — BLOOMBERG TERMINAL FOR INSECTS

Introduce live crypto market features and sensory encoding.

MQ-2.1 — VISUAL TRANSDUCTION

Restore the experimentally identified missing first-hop visual handoff.

Preserve the frozen biological connectome and transmitter signs while adding
the minimum modeled graded visual dynamics required for R1-R6 information to
propagate through the dominant L1/L2/L3/Lai relay.

MQ-2.1 parameters must be frozen independently of A/B market discrimination.

MQ-3 remains blocked until reproducible neural activity propagates beyond the
retinal population and required controls are repeated.

MQ-3 — EMPLOYEE HAS OPINIONS

Status: COMPLETE.

Establish an anatomy-first descending readout and test whether market-conditioned
sensory activity can reach that boundary reproducibly without neutral
contamination.

MQ-3 closed with a reproducible, sparse, strongly subthreshold DN-C1 response
under Condition A using the physiology-constrained MQ-3.2 visual propagation
model.

Targeted deletion of 13 preidentified first-onset pathway edges delayed all
9 original responder onsets, while 13 deterministic weight-matched sham
deletions altered 0 of 9 original onsets.

This supports causal necessity of those first-onset routes within the frozen
MoscaQuant computational model.

No financial semantics were assigned during MQ-3.

MQ-4 — NEUROSCOPE

Build detailed live neural visualization.

Status: COMPLETE.

MQ-5 — INTERVENTION AND PERTURBATION EXPERIMENTS

Test evidence-defined causal nodes and pathways using frozen intervention
protocols, controls, robustness checks, independent-runtime replication,
and read-only Neuroscope intervention replay.

Status: COMPLETE — ACCEPTED WITH DOCUMENTED LIMITATIONS.

MQ-6 — DEPLOY THE WARDEN

Deploy independent risk gateway and conduct adversarial testing.

REPOSITORY AUTHORITY BOUNDARY

Public moscaquant is authoritative for scientific configuration, protocols,
methods, accepted results, claim boundaries, reproducibility code, public-safe
evidence, and the open scientific Neuroscope viewer.

Private moscaquant-panopticon owns presentation/product implementation:
navigation, personnel/HR presentation, achievement UX/audio, preferences,
mobile UX, Broadcast/live-blog presentation, social adapters, community
presentation, and lore.

Private moscaquant-ops remains authoritative for WARDEN-01, private operational
ledgers, containment state, operational provenance, and private execution
plumbing.

Panopticon consumes scientific meaning from public-safe artifacts. It is not a
scientific authority.

PRESENTATION MAY INTERPRET EVIDENCE. IT MAY NEVER MANUFACTURE IT.

MQ-7 — AWAKEN THE ORACLE

Implement and validate the behavioral correction and behavioral-layer
protocols.

MQ-7.18 — PAIRWISE ROUTE INTERACTION — COMPLETE

Under the frozen condition-B SHOCK-56393 replay, MQ-7.18 tested all 45 unique
pairs among the ten frozen first-wave branches against the preregistered
independent-residual expectation:

    expected = 1 - (1 - A) * (1 - B)

Multiple pairs showed positive supra-independent interaction excess.

Strongest pair: 62598 + 77298
Observed pair attenuation: 0.47053613280033013
Independent-residual expectation: 0.4509162290662455
Interaction excess: 0.01961990373408462

The strongest negative interaction excess was approximately -0.000753.

Validated null-edge pair controls using 68045 -> 82348 produced maximum
absolute interaction excess 0.0.

CLASSIFICATION: PAIRWISE SUPRA-INDEPENDENT INTERACTION — SUPPORTED.

Claim boundary: this is a frozen-model interaction result. It does not
establish biological compensation, adaptive rerouting, biological learning,
or generalization beyond the tested replay.

MQ-7.19 — CONDITIONAL PAIRWISE CONTRIBUTION — COMPLETE

MQ-7.19 froze the three strongest positive MQ-7.18 pairs:

1. 62598 + 77298
2. 62598 + 79672
3. 79672 + 77298

Each tested direction showed positive conditional gain: each branch explained
a larger fraction of the remaining DN-C1 effect when its partner branch was
absent than its standalone attenuation alone predicted.

Validated null controls produced maximum absolute conditional gain 0.0.

CLASSIFICATION: CONDITIONAL COMPENSATION-LIKE DEPENDENCE — SUPPORTED.

The supported claim is bidirectional conditional dependence compatible with
compensation-like behavior within the frozen model.

It does not establish biological compensation, adaptive rewiring, homeostasis,
or living-fly behavior.

The MQ-7 causal-pathway subphase is CLOSED after MQ-7.19.

Blind triple or higher-order combinatorial searches require a new
independently motivated hypothesis and frozen protocol.


MQ-8 — CORPORATE CULTURE

Implement achievements, personnel records, reviews and related systems.

MQ-9 — OPEN THE PANOPTICON

Deploy the public spectator environment and Containment Chamber.

MQ-10 — INTRODUCE THE MONEY

Connect supported broker infrastructure in read-only mode.

MQ-11 — THE CASINO OPENS

Permit tiny controlled real-money transactions through WARDEN-01.

MQ-12 — CONSEQUENCES

Enable experimental plasticity and persistent aversive learning.

MQ-13 — MOSCA VS THE WORLD

Conduct comparative experiments against controls and benchmarks.

24.X. MQ-8 Achievement System

MQ-8 introduces a global achievement and narrative-observability system.

The achievement registry supports a maximum canonical namespace of:

128 ACHIEVEMENT DEFINITIONS

The initial MQ-8 release should target approximately 60 populated definitions.
Unused identifiers remain reserved for later roadmap phases and experimentally
validated behaviors.

Achievements are presentation and observability artifacts.

They do not create scientific evidence.

Every non-lore achievement must derive from at least one of:

- explicit recorded telemetry;
- a frozen experimental result;
- a preregistered control-supported result;
- a reproducible runtime or provenance event;
- an explicitly declared canonical project milestone.

Every unlock must be traceable to the data or project record that caused it.

Repeatable achievements are represented as independent append-only occurrence
records.

Stack counts are derived from occurrence history and are never treated as
primary scientific state.

Each occurrence must preserve, where applicable:

- achievement identifier and definition version;
- subject identifier;
- timestamp;
- experiment and session identifier;
- generation or frame;
- source event identifier;
- trigger version;
- stack index;
- relevant trigger measurements;
- artifact or evidence references;
- experiment seed;
- runtime profile;
- state hash;
- previous-occurrence hash.

Historical achievements discovered by replaying accepted experimental records
must be explicitly marked as HISTORICAL_REPLAY.

Project-level narrative milestones must be explicitly marked as MANUAL_CANON.

Achievements may unlock simultaneously from one source event.

Unless a frozen definition declares otherwise, one achievement does not suppress
another.

Achievement presentation may include humorous, cultural, science-fiction,
video-game, finance, internet, or project-specific references.

Narrative language must not alter the scientific interpretation of the source
event.

The achievement layer must maintain an explicit distinction between:

- SCIENCE
- ORACLE
- CONTAINMENT
- BEHAVIOR
- LORE
- SECRET / ODDITY

Every achievement must have exactly one canonical category.

Where useful, achievements should expose an evidence classification:

E0 — LORE ONLY
E1 — TELEMETRY DERIVED
E2 — EXPERIMENTALLY OBSERVED
E3 — CONTROL-SUPPORTED
E4 — REPLICATED

Evidence level describes provenance only.

It is not a score of importance.

The Panopticon achievement notification system must be global application
chrome.

Achievement notifications must be capable of appearing regardless of the page
currently being viewed, including science-facing Neuroscope and experimental
review pages.

Achievement notifications:

- must not alter experimental execution;
- must not alter scientific state;
- must not alter WARDEN-01 policy;
- must survive route changes;
- must queue simultaneous unlocks deterministically;
- must display repeat counts when applicable;
- must permit navigation to supporting evidence;
- must permit visual/audio muting without disabling event recording;
- must use original MoscaQuant visual, audio, animation, and interaction design.

The intended interaction may evoke the immediacy and persistence of classic
console achievement notifications, but protected artwork, sounds, layouts, or
trade dress must not be copied.

THE SCIENTIST MAY CLOSE THE POPUP.

THE SCIENTIST MAY NOT DELETE THE EVENT.

### MQ-8 Achievement Refinements

The 128-slot namespace is partitioned for operational clarity:

- ACH-001 through ACH-032 — SCIENCE
- ACH-033 through ACH-048 — ORACLE
- ACH-049 through ACH-064 — CONTAINMENT
- ACH-065 through ACH-088 — BEHAVIOR
- ACH-089 through ACH-112 — LORE
- ACH-113 through ACH-120 — ANOMALOUS OBSERVANCES / BLACKSITE HOLIDAYS
- ACH-121 through ACH-128 — SECRET / ODDITY

Reserved ranges organize identifiers only. They do not rank scientific importance.

Achievement definitions and achievement occurrences are distinct records.
Definitions describe deterministic trigger semantics. Occurrences record every qualifying event.

Repeatable achievements must preserve every occurrence. Stack counts, first-seen timestamps,
latest-seen timestamps, streaks, and milestone tiers are derived views over the immutable
occurrence history.

A single source event may unlock multiple achievements. All such occurrences must retain the
same source event identifier so later analysis can reconstruct co-occurrence.

Achievement trigger versions are immutable. A later trigger revision creates a new trigger
version and must not silently reinterpret historical occurrences.

Historical replay must be idempotent. Reprocessing the same source event under the same
achievement definition and trigger version must not create duplicate occurrences.

Presentation suppression does not suppress evidence. Reduced motion, muted audio,
presentation mode, route transitions, or closed notifications may hide or soften the popup,
but the underlying event remains recorded.

MQ-8 defines a Lore Firewall.

Every public-facing narrative achievement must maintain, where applicable:

- public_text;
- science_text;
- claim_boundary;
- evidence_refs.

Narrative language may be absurd. Scientific interpretation may not be.

MQ-8 personnel records, reviews, PIPs, promotions, demotions, commendations, and disciplinary
actions must be backed by explicit recorded events or declared manual canon. Corporate-HR
narrative may summarize evidence but may not invent behavioral facts.

HR records are separate from achievement records. Achievements may contribute evidence to
reviews, but a review is not itself an achievement occurrence.

ANOMALOUS OBSERVANCES is the canonical system name for temporary novelty-event days.
BLACKSITE HOLIDAYS is the approved public nickname.
An individual activation is a CONTAINMENT EVENT.
Community voting is presented as a PANOPTICON REFERENDUM.

Every Anomalous Observance must declare:

science_effect = NONE | PRESENTATION_ONLY | EXPERIMENTAL

Community-selected events default to PRESENTATION_ONLY.
Any EXPERIMENTAL event requires its own frozen protocol and may not enter the scientific record
through the entertainment layer alone.

Achievement notification delivery uses a deterministic global queue. When multiple unlocks
occur simultaneously, all events are recorded immediately and presentation order is
deterministic.

Presentation priority is:

SECRET / ODDITY
LEGENDARY
SCIENCE
CONTAINMENT
ORACLE
BEHAVIOR
LORE

Presentation priority affects display order only. It does not change evidence, causality, or
scientific importance.

The global achievement overlay has two required surfaces:

1. a brief application-wide toast;
2. a detailed achievement dossier.

The dossier must expose, where available:

- first occurrence;
- latest occurrence;
- total occurrence count;
- complete occurrence history;
- trigger definition and version;
- evidence level;
- source-event linkage;
- experiment/session/generation;
- supporting measurements;
- source artifacts;
- co-occurring achievements.

The toast may be obnoxious.
The dossier must have receipts.

At least one valid achievement definition must remain deliberately unreachable as a registry
and UI test case.

ACH-128 is reserved for this purpose.
Its canonical title is HALF-LIFE 3 CONFIRMED.
Its trigger is permanently false.
Its public text is: Nice try.
Its evidence level is E0 — LORE ONLY.
Its permanent locked state is intentional and must not be bypassed by historical replay,
community voting, manual telemetry injection, or ordinary runtime events.

MQ-8 PANOPTICON 3D CONTAINMENT PRESENTATION CANON

The future 3D containment space is a Panopticon presentation surface.

It may dramatize accepted scientific, behavioral, containment, achievement,
HR, Broadcast, and public-safe market state.

It is not a scientific authority, Warden authority, Oracle authority, or
broker command surface.

MQ-001 / MORTY SHALL be visually embodied at the trading desk.

The chained-to-the-trading-desk presentation is canonical visual language.
The chain is a presentation element only and has no operational authority.

MORTY SHALL wear the corporate tie.

MORTY's asymmetric eye presentation SHALL preserve the established retinal-map
coverage:

LEFT:
- 1,085 R1-R6 receptors
- 292 represented columns

RIGHT:
- 2,156 R1-R6 receptors
- 508 represented columns

The asymmetry represents retinal-map coverage and SHALL NOT be presented as a
claim that the biological right eye is literally twice the anatomical size of
the left eye.

The established asymmetric visual identity is the o_0 presentation.

Eye degradation, loss, dimming, deformation, or other renderer effects MAY
reflect sanitized active-neuron / retinal telemetry.

The renderer SHALL NOT invent neuron loss or feed visual state back into the
scientific runtime.

WARDEN-01 / Senator Armstrong and SCIENCE-01 / Placeholder McDoctorate SHALL
occupy the elevated observation-window / overlook as shadowed supervisory
figures.

WARDEN-01 / Senator Armstrong SHALL read immediately as physically imposing:
an exaggeratedly muscular, broad-shouldered silhouette consistent with the
project's Senator Armstrong visual joke.

SCIENCE-01 / Placeholder McDoctorate remains a less imposing academic /
reviewer silhouette whose visual language emphasizes observation, notes, and
skepticism rather than physical authority.

Their presentation MAY animate in response to public-safe state.

Examples include:

WARDEN-01:
- watching;
- arms crossed;
- leaning forward;
- containment response.

SCIENCE-01:
- watching;
- taking notes;
- skeptical reaction;
- facepalm.

These reactions are presentation only and grant no new authority.

ORACLE-01 / GLaDOS SHALL receive a deliberately excessive dramatic entrance
when the Sugar Cube Protocol begins.

ORACLE-01 / GLaDOS SHALL be presented as explicitly female / feminine-coded in
the Panopticon visual layer while remaining an artificial / mechanical Oracle
entity rather than a human scientific actor.

The canonical presentation sequence MAY include:

1. red-alert alarms;
2. emergency lighting;
3. screen override;
4. observation-window blackout;
5. mechanical / theatrical entry;
6. protocol reveal;
7. intervention presentation;
8. recovery / exit.

The renderer receives an already-authorized Sugar Cube / D6 event.

The renderer SHALL NOT roll the D6, choose a punishment, administer an
intervention, or modify Oracle state.

Decorative containment-room objects are explicitly permitted.

Examples include:

- coffee cups;
- trading-desk clutter;
- achievement trophies;
- warning placards;
- sugar-cube containers;
- market displays;
- fake corporate awards;
- motivational posters, including the intentionally ridiculous lady-fly
  bikini poster;
- other lore props consistent with Panopticon presentation.

Decor MAY react to state.

Decor SHALL NOT create state.

The 3D renderer SHALL consume sanitized, versioned presentation state and
remain renderer-independent.

Three.js, WebGPU, Godot, Unreal, or another renderer MAY replace one another
without changing scientific meaning.

The 3D renderer MUST NOT:

- mutate the connectome;
- change scientific configuration;
- administer experimental perturbations;
- enable or disable trading;
- place or cancel broker orders;
- change WARDEN-01 state;
- rewrite scientific, achievement, HR, or Broadcast evidence;
- expose private broker credentials, account identifiers, private Warden
  ledgers, private runtime paths, or other containment secrets.

SCENE STATE MAY REFLECT REALITY.

SCENE STATE MAY NOT CREATE REALITY.

CONTAINMENT ROOM VISUAL DENSITY AND HUD CANON

The 3D containment space SHALL preserve a clear visual hierarchy:

1. MQ-001 / MORTY;
2. the trading desk;
3. the observation window;
4. environmental lore and decorative props.

Persistent environment props MAY include:

- a coffee cup;
- a dead office plant;
- a cheap analog wall clock;
- a WARDEN warning placard;
- a sugar-cube container;
- a small performance-review / HR corkboard;
- an Employee of the Month frame featuring MQ-001;
- a red containment phone;
- a compact analog MORALE gauge;
- the approved ridiculous lady-fly motivational poster.

The MORALE gauge is intentionally non-scientific corporate theater.
Approved presentation labels MAY include:

- OPTIMAL;
- CONCERNING;
- UNIONIZING;
- REDACTED.

The red containment phone SHALL remain visually quiet during normal operation.
It MAY illuminate or animate during containment, Oracle, or incident events.
It SHALL NOT function as a real operational control.

Environmental state-reactive effects MAY include:

- desk-lamp flicker during elevated stress;
- coffee-level depletion during fatigue;
- monitor scanline or static effects during punishment;
- a subtle spotlight or visual emphasis on the motivational poster during
  elevated courtship / arousal presentation state;
- increased visibility or movement of observation-window silhouettes during
  significant events.

Rare event gags MAY include:

- sprinkler mist during a major incident;
- a temporary achievement banner;
- a small corporate confetti effect after promotion or major achievement;
- a MANDATORY MORALE IMPROVEMENT indicator after punishment.

Rare event gags SHOULD remain rare.
Only one dominant environmental gag SHOULD compete for attention at a time.

The persistent MQ-001 mood indicator SHALL use an original low-frame,
pixel-art fly portrait inspired by the concept of classic status-face HUDs
without copying protected artwork.

The pixel HUD SHALL mirror the current public-safe 3D presentation state,
including where applicable:

- hunger;
- arousal;
- courtship drive;
- threat / stress;
- fatigue;
- reward;
- punishment;
- Sugar Cube / abnormal state;
- current gross pose or action category.

The pixel HUD SHALL update at a deliberately slower visual cadence than the
full 3D renderer.

The HUD is a compressed presentation of already-derived state.
It SHALL NOT independently infer or create scientific state.

Numeric telemetry SHALL remain available alongside the mood portrait.

The governing clutter rule is:

MORTY FIRST.
THE DESK SECOND.
THE WINDOW THIRD.
THE ROOM SUPPORTS THE JOKE.

25. Go / No-Go Gates

MQ-3 cannot begin until market-driven activity propagates reproducibly beyond
the artificial retinal population into downstream connectome circuitry.

MQ-2.1 visual-transduction parameters must be frozen without reference to A/B
market discrimination, trading behavior, P&L, or a financial decoder.

Broker execution cannot begin until WARDEN-01 passes adversarial testing.

Plasticity cannot begin until frozen-connectome behavior is reproducible.

Public claims cannot imply the connectome constitutes a complete biological
simulation.

Performance claims cannot infer profitability from insufficient samples.

MQ-001 can never receive direct execution authority.

Any material neural-dynamics replacement introduced to restore downstream
propagation must pass its precommitted neutral-contamination gate before
market-conditioned A/B responses are inspected.

26. Success Levels

LEVEL 1 — CONTAINED
Connectome successfully loaded.

LEVEL 2 — ALIVE
Neural simulation responds to stimulus.

LEVEL 3 — MARKET AWARE
Market changes produce reproducible neural responses that propagate beyond the
artificial retinal population into downstream connectome circuitry.

LEVEL 4 — OPINIONATED
MQ-001 generates autonomous financial decisions.

LEVEL 5 — EMPLOYED
Real trades occur behind WARDEN-01.

LEVEL 6 — TRAINABLE
Consequences measurably alter future behavior.

LEVEL 7 — BIOLOGY MATTERS
Real topology meaningfully differs from randomized topology.

LEVEL 8 — PROFITABLE
Persistent positive risk-adjusted live performance.

LEVEL 9 — ANOMALOUS
MQ-001 consistently defeats serious controls.

LEVEL 10 — [REDACTED]
Performance exceeds expected parameters and its cause is unknown.

At Level 10:

NEURAL MODIFICATION ........ SUSPENDED
WARDEN-01 .................. ACTIVE
ORACLE ..................... ARMED

MANAGEMENT COMMENT:

THIS WAS SUPPOSED TO BE FUNNY.
27. Commandments

I. THOU SHALT NOT GIVE THE MOSCA LEVERAGE.

II. THOU SHALT HONOR THE DAILY LOSS LIMIT.

III. THOU SHALT NOT OVERRIDE THE ORACLE.

IV. THOU SHALT LOG ALL STUPIDITY.

V. THOU SHALT DISTINGUISH ALPHA FROM RANDOM LUCK.

VI. THOU SHALT MAINTAIN EXPERIMENTAL CONTROLS.

VII. THOU SHALT NEVER GIVE THE MOSCA 0DTE OPTIONS.

VIII. THOU SHALT RESPECT SUGAR CUBE MODE.

IX. IF SHUFFLED MOSCA WINS, THOU SHALT ADMIT IT.

X. IF MQ-001 BECOMES CONSISTENTLY PROFITABLE, THOU SHALT REFER TO HIM AS
FUND MANAGER.

28. Change Control

This charter is intentionally resistant to uncontrolled feature expansion.

A proposed addition should normally satisfy at least one of the following:

resolves an implementation roadblock;
improves experimental validity;
improves containment or safety;
improves observability;
improves reproducibility;
materially improves the public experimental interface;
replaces an assumption invalidated by evidence.

Everything else belongs in:

BACKLOG_OF_QUESTIONABLE_IDEAS.md

Architecture decisions that materially alter the project should receive an
Architecture Decision Record under docs/decisions/.

The canonical project retrospective and approved highlight-reel narrative is:

docs/retrospectives/MOSCAQUANT_EXPERIMENTAL_HIGHLIGHT_REEL.md

The retrospective may summarize accepted scientific results and their approved
lore/comedic framing, but it does not replace frozen experiment protocols,
result records, or claim boundaries.

Its DOCX companion is a rendered distribution artifact. The Markdown source is
authoritative for retrospective content.

Git history is the authoritative project record.

## HAHN — HUMAN RESOURCES / CORPORATE CULTURE

HAHN is the canonical Human Resources and corporate-culture persona for MQ-8.8.

Identity and presentation canon:

- codename: HAHN;
- role: Head of Human Resources / Personnel Operations;
- real-world participation: project collaborator participating in MoscaQuant by choice;
- visual presentation: glamorous, fashion-forward, fitness-influencer energy;
- personal flavor: fitness culture and enthusiastic pickleball fandom;
- demeanor: polished, composed, intimidatingly professional, and fully committed to
  treating MoscaQuant's absurd containment workplace as if it were a serious corporate
  HR environment.

Narrative function:

- HAHN owns the personnel / HR presentation layer;
- HAHN may issue or present evidence-backed COMMENDATION, PROMOTION, DEMOTION, PIP,
  DISCIPLINE, and REVIEW records;
- HAHN may comment on personnel history and corporate culture;
- HAHN may participate in comedic HR framing, including scheduling formal reviews,
  documenting misconduct, and treating MQ-001 as an employee subject to policy.

Authority boundary:

- HAHN has no scientific authority;
- HAHN has no ORACLE perturbation authority;
- HAHN has no WARDEN financial or containment authority;
- HAHN has no broker or trading authority;
- HR records must remain evidence-linked presentation records and must not create,
  modify, or reinterpret achievement occurrences or scientific results.

Character interaction principle:

MORTY may fear GLaDOS, respect Senator Armstrong's financial authority, and still
dread the phrase: "Hahn would like a quick conversation with HR."

29. Current Directive

**Current implementation directive:** complete MQ-8.9 — PANOPTICON
BROADCAST SYSTEM next. MQ-9 remains gated until MQ-8 requirements are satisfied.

YOLO & HODL LLC
MOSCAQUANT

SUBJECT ................. MQ-001
CURRENT PHASE ........... MQ-8 / CORPORATE CULTURE
NEXT PHASE .............. MQ-9 / OPEN THE PANOPTICON
MISSION ................. MQ-8 / ACHIEVEMENTS, PERSONNEL, REVIEWS, AND RELATED SYSTEMS

BROKER .................. NONE
TRADING AUTHORITY ....... NONE
ORACLE .................. ACTIVE / MQ-7 COMPLETE
WARDEN-01 ............... MQ-6 COMPLETE / LOCAL AUTHORITY SERVICE
PANOPTICON .............. BASELINE DEPLOYED / MQ-9 NOT YET COMPLETE

CONTAINMENT ............. ACTIVE

FINANCIAL SEMANTICS ..... NOT ASSIGNED

CURRENT DIRECTIVE:

MQ-8 SHALL IMPLEMENT AN APPEND-ONLY, EVIDENCE-BACKED ACHIEVEMENT SYSTEM WITH A
128-DEFINITION CANONICAL NAMESPACE.

ACHIEVEMENT STACKS SHALL PRESERVE EVERY UNDERLYING OCCURRENCE AND ITS SUPPORTING
TELEMETRY OR PROJECT RECORD.

THE GLOBAL PANOPTICON ACHIEVEMENT OVERLAY MAY INTERRUPT THE SCIENTIST'S SCREEN.

IT MAY NOT INTERRUPT THE SCIENCE.

PRESERVE THE ACCEPTED MQ-5 SCIENTIFIC RECORD AND ITS CLAIM BOUNDARIES.
PRESERVE WARDEN-01 AS AN INDEPENDENT AUTHORITY BOUNDARY.
MQ-7 COMPLETED ORACLE-01 AND THE VALIDATED D6 BEHAVIORAL INTERVENTION SYSTEM.
MQ-8 MAY ADD ACHIEVEMENTS, PERSONNEL RECORDS, REVIEWS, PIPS, AND NARRATIVE TELEMETRY.
MQ-8 PRESENTATION MUST NOT ALTER SCIENTIFIC STATE, HISTORICAL RECORDS, WARDEN POLICY, OR EXPERIMENTAL CLAIMS.
PRE-MQ-12 PLASTICITY EXPERIMENTS ARE SCIENTIFIC GROUNDWORK ONLY AND DO NOT CONSTITUTE COMPLETION OR ACTIVATION OF MQ-12.
NO FINANCIAL OR TRADING SEMANTICS ARE RETROACTIVELY ASSIGNED TO MQ-1 THROUGH MQ-7.

Past performance does not guarantee future sugar cubes.
---

## MQ-4 Closure and MQ-5 Entry

**Canonical status date:** 2026-09-16

### MQ-4 — Neuroscope

MQ-4 is **COMPLETE and ACCEPTED**.

Neuroscope is the read-only visualization and inspection layer for the
frozen MQ-1 through MQ-3 experimental state.

Accepted MQ-4 capabilities include:

- hybrid anatomical visualization
- explicit distinction between MaleCNS `somaLocation` and
  non-anatomical `topologyFallback`
- interactive neuron inspection
- role filtering
- 192-frame replay exploration
- recorded activity visualization
- frozen MQ-3.2 causal-edge inspection
- causal graph traversal
- nine-neuron responder isolation
- responder peak analysis
- synchronized responder activity plotting
- integrated operator documentation

Accepted dataset invariants are:

- 12,475 selected neurons
- 7,486 real soma positions
- 4,989 topology fallbacks
- 13 preserved causal edges
- 9 causal responders
- 192 replay frames

MQ-4 does not alter experimental state.

Replay remains recorded telemetry rather than a new simulation.

Causal traversal and visualization do not create additional causal
evidence.

Topology fallback geometry remains explicitly non-anatomical.

The accepted MQ-4 record is:

`docs/experiments/mq4-acceptance.md`

The operator-facing Neuroscope guide is available from the visualization
and is also documented in:

`docs/neuroscope-guide.md`

### MQ-5 — Intervention and Perturbation Experiments

MQ-5 advances the experiment itself rather than extending Neuroscope as
a visualization product.

The purpose of MQ-5 is to test whether controlled interventions on
previously identified causal nodes and pathways produce reproducible,
measurable downstream changes relative to appropriate controls.

MQ-5 begins from the frozen evidence produced by MQ-1 through MQ-3.
MQ-4 provides the inspection instrument but is not the experiment
engine.

#### Core question

Given the causal structure identified before MQ-5, what happens when
specific nodes, edges, or defined pathway components are deliberately
perturbed under controlled experimental conditions?

#### Initial experimental scope

MQ-5 may evaluate interventions involving:

- individual causal source neurons
- intermediate causal-path neurons
- responder-associated inputs
- explicitly defined multi-hop causal paths
- appropriate sham or matched control interventions

Candidate interventions must be selected from established experimental
artifacts or by a separately documented selection rule.

They must not be chosen retroactively because a result looks
interesting.

#### Required controls

Every intervention experiment must define its control before results are
interpreted.

Controls may include, where scientifically appropriate:

- sham intervention
- matched non-causal intervention
- unchanged baseline replay
- timing-shifted control
- strength-matched control

The specific control belongs to the experiment definition and must not
be selected after seeing the outcome.

#### Required measurements

MQ-5 experiments must record enough information to distinguish:

- intervention target
- intervention type
- intervention magnitude
- intervention timing
- baseline state
- downstream activity
- responder activity
- latency
- effect duration
- control outcome

Metrics and measurement windows must be defined before an intervention
is judged.

#### Causal discipline

MQ-5 must preserve the distinction between:

1. previously established causal evidence,
2. the intervention being introduced,
3. the observed downstream response, and
4. any new causal conclusion supported by that experiment.

A visually compelling response is not by itself sufficient evidence.

New causal claims require a documented experimental comparison against
the predefined control.

#### Reproducibility

An MQ-5 result is not accepted solely because a single intervention run
produces the expected direction of effect.

Experiments must define reproducibility requirements before acceptance.

Randomness, seeds, runtime parameters, machine configuration, and
scientific configuration must remain separable and auditable.

#### Neuroscope boundary

Neuroscope may visualize MQ-5 intervention results.

Neuroscope must not silently become the mechanism that changes the
scientific state.

Intervention execution belongs to the experimental pipeline.

Visualization remains an interpretation layer.

#### Runtime portability

MQ-5 continues the existing separation between:

- scientific configuration
- experiment configuration
- runtime / machine configuration

Migration from Habitat to another workstation or cloud runtime must not
silently alter scientific semantics or expected outputs.

Before a new workstation, cloud worker, or other runtime profile becomes an
authoritative scientific execution environment, it must pass a frozen
runtime-parity acceptance check.

Where practical, that check compares:

- scientific artifact and configuration hashes;
- frozen stimulus identity;
- deterministic neural outputs or equivalent scientific outputs;
- selected responder values;
- accepted causal-result identity;
- runtime-profile metadata.

A hardware migration that changes scientific output is a scientific change,
not an infrastructure-only migration.

#### Entry condition

MQ-5 implementation must begin with a written experimental protocol.

Before intervention code is accepted, that protocol must identify:

- hypothesis
- intervention target-selection rule
- intervention mechanism
- control
- measurement window
- outcome metrics
- reproducibility requirement
- acceptance / rejection criteria
- generated artifact names and versions

No intervention result should determine its own success criterion.

#### Financial semantics

Financial and trading semantics remain:

**NOT ASSIGNED**

MQ-5 is a neuroscience / computational experiment phase.

No market action, asset interpretation, position sizing, or trading
behavior is inferred from neural responses during this phase.

### Phase transition

The canonical project transition is now:

**MQ-1–MQ-3 frozen experimental evidence → MQ-4 accepted Neuroscope → MQ-5 controlled intervention experiments**

MQ-4 answers:

> What happened, where did it happen, and how can we inspect the evidence?

MQ-5 asks:

> What changes when we deliberately intervene on that evidence-defined system?

**Anatomy. Evidence. Causality. Next.**

## Current Cloud Deployment Architecture

Canonical public URL: **https://moscaquant.com**

Current deployment uses a cost-conscious AWS baseline host while preserving logical service boundaries.

```text
Internet
   |
   v
Route 53 / TLS
   |
   v
https://moscaquant.com
   |
   v
Public Web Surface
   |
   +-- MQ-001 runtime
   |
   +-- WARDEN-01
          local IPC only
          no public TCP service
          no broker credentials
          no exchange credentials
          no wallet credentials
```

Future heavy compute may move to ephemeral workers without changing scientific configuration or accepted experimental semantics.

A future Execution Adapter remains a separate architectural layer and is **NOT IMPLEMENTED**.

**External execution: DISABLED**

**Financial semantics: NOT ASSIGNED**

## MQ-6 Canonical Authority and Execution Boundary

MQ-6 is **COMPLETE**. WARDEN-01 completed its local authority-boundary and production-containment program with **191 / 191 tests passed** under tested local conditions.

Accepted MQ-6 capabilities include exact authority accounting, durable replay protection, fail-closed persistence, versioned `warden-interface-v1`, sanitized telemetry, local Unix-domain-socket IPC, OS-derived peer identity, socket containment, tamper-evident audit chaining, generated adversarial testing, real SIGKILL/restart resilience, resource-pressure testing, and hardened supervisor/OS sandboxing.

Canonical architecture:

`MQ-001 / MoscaQuant -> WARDEN-01 -> Future Execution Adapter -> Broker / Exchange`

WARDEN-01 owns authorization, accounting, replay protection, persistence, and audit evidence. It does **not** require broker credentials, exchange credentials, wallet credentials, public Internet connectivity, broker SDKs, or exchange SDKs.

External execution, if later authorized by the roadmap, belongs to a separate execution adapter. Future reporting must distinguish MQ-001 proposals, Warden approvals/denials, executor behavior, and realized external outcomes.

MQ-6 does not alter the accepted MQ-1 through MQ-5 scientific record.

**Financial semantics remain: NOT ASSIGNED**

**External execution remains: DISABLED**

## Methodological Hardening After MQ-4

The progression into MQ-5 does not change the frozen MQ-1 through MQ-3
evidence or the pre-registered MQ-5.1 intervention protocol.

The following project-level safeguards apply to future MoscaQuant phases.

### Internal causality is not biological validation

A successful intervention establishes a causal relationship within the
specified MoscaQuant model.

It does not, by itself, establish equivalent causal behavior in a living
Drosophila nervous system.

Claims must preserve the distinction between:

- structural connectivity,
- simulated dynamical causality,
- biological causality,
- financial interpretation.

Biological causality must not be claimed without evidence appropriate to
that claim.

### Independent-runtime replication

Re-running identical code proves implementation reproducibility, not
independent scientific replication.

Where practical, important causal findings should later be reproduced
using an independently implemented runtime or reduced-circuit reference
implementation.

Independent replication must preserve the scientific configuration while
remaining implementation-independent.

### Null-model diversity

Claims that MaleCNS topology itself matters must not depend on comparison
against only one randomized graph.

Before strong topology-specific conclusions are permitted, future control
work should include multiple scientifically defensible null families where
practical, including examples such as:

- degree-preserving rewiring,
- sign-preserving rewiring,
- weight-distribution-preserving controls,
- cell-class-constrained controls,
- spatially constrained controls where appropriate.

Exact null families must be defined before their confirmatory results are
interpreted.

### Sensory-encoding robustness

Market-to-sensory encoding is an experimental design choice.

A causal pathway that appears under only one arbitrary encoding must not
automatically be described as a general property of the connectome.

Later phases should test whether important findings survive reasonable
alternative sensory encodings while holding the neural substrate fixed.

### Exploratory and confirmatory separation

Exploratory observations are allowed and encouraged, but they must be
labeled exploratory.

Targets, thresholds, controls, or hypotheses discovered after inspecting
results must not be represented as pre-registered confirmatory tests.

Protocol amendments must remain recoverable through Git history.

### Negative-results policy

Failed, null, opposite-direction, and inconclusive experiments are part of
the scientific record.

They must not be hidden, silently discarded, or omitted merely because
they weaken a preferred narrative.

The meme layer may joke about failure.

The scientific layer must preserve it.

### Claims ledger

Before financial semantics are assigned, MoscaQuant should maintain a
machine- or human-readable claims ledger recording:

- the claim,
- supporting evidence,
- current status,
- permitted wording,
- prohibited or unsupported wording,
- the phase in which the claim became justified.

The purpose is to prevent conclusions from silently expanding beyond the
evidence that supports them.

### Warden attribution boundary

When real-money phases eventually exist, performance must be attributable
to the correct system component.

At minimum, reporting must distinguish:

- raw MQ-001 proposals,
- WARDEN-01 accepted proposals,
- WARDEN-01 rejected proposals,
- actually executed trades.

WARDEN-01 risk logic must not be mistaken for neural-model performance.

### Scientific identity

MoscaQuant intentionally combines absurd presentation with conservative
experimental practice.

The humor may escalate.

The evidentiary standard must not relax.

Financial semantics remain:

**NOT ASSIGNED**

## MQ-5 Acceptance State

MQ-5 completed formal acceptance review after MQ-5.7.

Acceptance audit result:

- checks: 75
- passed: 75
- failed: 0

MQ-5 classification:

**COMPLETE — ACCEPTED WITH DOCUMENTED LIMITATIONS**

Acceptance confirms that the frozen MoscaQuant simulation evidence,
implementation controls, artifact-integrity requirements, Neuroscope
read-only boundary, and claim restrictions were satisfied.

Acceptance does not convert unresolved confounds into resolved ones.

The project must continue to preserve the distinction between:

- simulated causal structure,
- implementation reproducibility,
- robustness to tested alternatives,
- biological causality,
- financial usefulness.

Biological causality remains:

**NOT CLAIMED**

Financial semantics remain:

**NOT ASSIGNED**

---

## MQ-5 Evidence State Through MQ-5.6

This section records the durable scientific state reached before MQ-5.7.

It does not replace the individual preregistrations or result artifacts.

### Generalized intervention evidence

Across the 13 frozen MQ-3 causal edges:

- 13 / 13 retained monotonic dose-response behavior,
- 12 / 12 edges with prospectively valid matched controls showed a larger
  causal-source intervention effect than the matched non-causal control,
- 3 / 13 causal-frame interventions exceeded the nearby timing control,
- 10 / 13 nearby timing controls produced equal or larger effect magnitude,
- 7 / 13 full source-silencing interventions delayed first downstream
  response.

The timing result must not be rewritten as single-frame temporal
exclusivity.

The supported interpretation is that the frozen causal frames identify
causal onset or evidence points within broader active causal windows.

### Multi-hop pathway evidence

The frozen pathway:

`56393 → 68045 → 1273`

retained dose-dependent propagation through the intermediate node.

Attenuating the upstream source reduced the intermediate state and then the
downstream response.

Attenuating the intermediate node independently reduced the downstream
response.

This supports causal propagation within the frozen simulation model.

It does not establish equivalent biological propagation in a living fly.

### Convergence evidence

The frozen convergence systems:

- `44274 + 55925 → 55`
- `55548 + 87441 → 51`
- `92657 + 93484 → 129`

all retained:

- independent contribution from each frozen input,
- combined perturbation exceeding either individual perturbation,
- monotonic combined dose response.

No statistical synergy, antagonism, subadditivity, or superadditivity label
is assigned without a separately preregistered interaction test.

Responder 51 remains subject to its documented extremely-small numerical
scale.

### Sensory-normalization robustness

CONF-004A replaced the original causal rolling mean / standard-deviation
normalizer with a causal rolling median / MAD normalizer while holding the
remaining scientific configuration fixed.

The alternative representation materially changed sensory and network
activity.

Nevertheless:

- 13 / 13 frozen causal sources remained engaged,
- 12 / 12 frozen matched controls remained engaged,
- generalized single-node results retained the same categorical pattern,
- the two-hop pathway retained its qualitative and quantitative structure,
- all three convergence systems retained their qualitative structure.

Median Encoder-B / Encoder-A absolute full-silencing effect ratio across the
generalized edge set was approximately:

`1.00007`

This supports robustness to the tested normalization alternative.

It does not establish general sensory-encoding independence.

### Independent-runtime replication

MQ-5.6 reproduced selected accepted causal findings through a separately
implemented full-network reference runtime.

The independent runtime did not inherit from or call:

- the production visual-transduction runtime,
- the production physiology-constrained runtime,
- the MQ-5 intervention runtime.

Before outcome generation, numerical comparison tolerances were frozen as:

- absolute tolerance: `1e-12`
- relative tolerance: `1e-6`
- small-value threshold: `1e-12`

Selected replication targets were:

- direct edge: `43417 → 656`
- pathway: `56393 → 68045 → 1273`
- convergence: `44274 + 55925 → 55`

All predefined replication gates passed:

- frozen artifacts unchanged,
- direct numeric replication,
- pathway numeric replication,
- convergence numeric replication,
- convergence combined-dose monotonicity,
- convergence combined effect exceeding either single input.

This materially reduces concern that the selected MQ-5 findings are artifacts
of one neural-runtime implementation.

It remains replication within the same frozen mathematical model.

### Current claim boundary

The following wording is supported:

> Selected causal effects are reproducible within the frozen MoscaQuant
> simulation model across the production runtime, a tested alternative
> normalization scheme, and an independently implemented full-network
> reference runtime.

The following wording is not supported:

- MoscaQuant has established biological causality in living Drosophila.
- The findings are independent of all sensory encodings.
- The validated responder ensemble represents all descending neurons.
- MaleCNS topology has been established as uniquely responsible relative to
  all appropriate null-model families.
- The neural findings have demonstrated predictive trading value.
- The neural findings have demonstrated profitability.

Financial semantics remain:

**NOT ASSIGNED**

---

## Panopticon Public Experiment and Entertainment Layer

MoscaQuant is simultaneously:

1. a serious experimental project,
2. an intentionally absurd public spectacle.

These roles may coexist only if their boundaries remain explicit.

The entertainment layer must never silently alter the scientific record.

### Special Days

The Panopticon may host clearly labeled novelty or exploratory
perturbations known publicly as **Special Days**.

Example public modes include:

- Left Eye Day,
- Right Eye Day,
- Super Genius Day,
- Cocaine Day,
- Constant Orgasm Day,
- Sleep-Deprived Fly Day,
- Sedated Fly Day,
- Sensory Deprivation Day,
- White Noise Day,
- Groundhog Day,
- Everything Is DOGE Day,
- Half-Brain Day,
- Management Consultant Day,
- Latency From Hell Day,
- Glitch in the Matrix Day.

These names are entertainment labels.

Where useful, a Special Day should also expose a sober scientific alias
describing the actual perturbation.

Examples:

- `LEFT EYE DAY`
  -> unilateral sensory-input restriction

- `CONSTANT ORGASM DAY`
  -> sustained reward-saturation perturbation

- `MANAGEMENT CONSULTANT DAY`
  -> constrained topology-randomization control

- `GROUNDHOG DAY`
  -> repeated-input state-dependence experiment

The public name may be ridiculous.

The underlying perturbation definition must not be ambiguous.

### Special-Day scientific status

Special Days default to:

**EXPLORATORY / ENTERTAINMENT**

They are not confirmatory experiments merely because they produce
interesting behavior.

Special-Day telemetry must remain distinguishable from:

- frozen baseline telemetry,
- pre-registered experiments,
- confirmatory intervention results,
- evidence used to support scientific claims.

A Special Day may later motivate a formal scientific experiment.

If so, the resulting hypothesis, controls, targets, timing, and outcome
criteria must be defined separately before confirmatory data are
examined.

Public engagement must never retroactively convert an exploratory result
into a pre-registered one.

### Community voting

The Panopticon may allow authenticated users to vote on upcoming
Special Days, novelty experiments, presentation themes, or other
non-confirmatory activities.

Community voting may influence what exploratory entertainment experiment
is performed next.

Community voting must not determine:

- whether a scientific result is published,
- which confirmatory results are retained,
- whether a failed experiment is hidden,
- scientific thresholds after results are known,
- the interpretation of frozen evidence.

Money or popularity may select the next joke.

They may not select the conclusion.

### Authentication and privacy

OAuth or equivalent authentication may be used for voting,
anti-abuse controls, supporter identity, or community features.

MoscaQuant should request the minimum practical authentication scope.

User information should be collected only when it has a defined product
purpose.

The Panopticon must clearly disclose what information is collected and
why.

Authentication data, supporter data, community data, and scientific
telemetry are separate concerns.

User identity must not become an implicit scientific variable.

### Monetization

MoscaQuant is permitted to generate revenue.

Potential mechanisms include:

- voluntary donations,
- supporter memberships,
- merchandise,
- sponsorships,
- premium presentation or historical telemetry access,
- community-driven novelty-event sponsorship,
- research sponsorship.

Monetization must not alter scientific reporting.

Sponsors, donors, voters, supporters, or customers receive no right to:

- suppress results,
- rewrite hypotheses after outcomes are known,
- hide negative findings,
- change frozen experimental evidence,
- convert exploratory observations into confirmatory claims.

Commercial success is not scientific evidence.

Scientific failure is not commercial failure.

### WARDEN-01 and financial attribution

Future real-money operation must preserve explicit attribution between:

- raw MQ-001 proposals,
- WARDEN-01 approved proposals,
- WARDEN-01 rejected proposals,
- executed trades,
- realized financial outcomes.

WARDEN-01 must not accidentally become the profitable strategy while
MQ-001 receives the scientific or public credit.

The brain proposes.

The Pi disposes.

### Fly Wife's Boyfriend Capital

Public-facing MoscaQuant language may refer to future experimental
capital as:

**FLY WIFE'S BOYFRIEND CAPITAL**

This is a meme-layer term only.

Formal experiment and risk artifacts must use precise financial and risk
terminology.

Financial semantics remain:

**NOT ASSIGNED**

until the corresponding project gate is explicitly passed.

### MQ-001 presentation canon

When MQ-001 receives a full-body Panopticon representation, the canonical
presentation includes a tie.

The presentation layer may be absurd.

The scientific artifacts remain boring.

## Statistical Discipline, Confounds, and Stopping Rules

MoscaQuant must define the rule used to classify an experiment before
examining the result that rule will classify.

### Statistical decision discipline

A statistical method must match the actual experimental unit and control
design.

MoscaQuant must not manufacture rigor by treating dependent neurons,
frames, or repeated observations as independent samples merely because
doing so produces a convenient p-value.

Where appropriate, analysis should prefer:

- explicit effect sizes,
- uncertainty intervals,
- permutation or randomization tests,
- null distributions generated by the experimental control design,
- tests that preserve known dependence structure.

The exact statistical rule for a confirmatory experiment must be frozen
before its confirmatory outcome is inspected.

No statistical threshold may be selected because it produces a preferred
classification.

### Known-confounds register

Claims and limitations are separate records.

The claims ledger records what available evidence supports.

The known-confounds register records unresolved reasons an interpretation
could still be incomplete, fragile, or wrong.

Open confounds must remain visible until explicitly mitigated or resolved.

A limitation must not disappear merely because later experiments become
more interesting.

### Hypothesis-family stopping rules

MoscaQuant must not indefinitely modify an encoder, decoder, control, or
analysis until a desired result appears.

For research programs involving repeated attempts against a common
hypothesis, a stopping or falsification rule should be defined before
confirmatory testing begins.

When the pre-registered stopping condition is reached, the corresponding
claim is classified unsupported.

A genuinely new hypothesis may begin a new experimental program only if
it is defined prospectively and is not a disguised continuation of failed
post-hoc tuning.

### Financial-validation boundary

Neural activity is not evidence of financial usefulness.

Before financial semantics may be assigned, MoscaQuant must demonstrate
performance using real historical market data under a frozen validation
protocol.

That protocol must include appropriate controls for:

- look-ahead bias,
- test-set leakage,
- transaction costs,
- slippage,
- temporal non-stationarity,
- trivial benchmark strategies,
- randomized or shuffled controls.

The final held-out evaluation period must not become another development
set.

### WARDEN-01 adversarial validation

Before WARDEN-01 is permitted to authorize real-money actions, its safety
protocol must be pre-registered.

Attack scenarios and pass/fail conditions must be written before final
safety evaluation.

WARDEN-01 follows the principle:

**Ambiguous state fails closed.**

Adversarial validation should include, where applicable:

- duplicate proposals,
- replayed proposals,
- stale proposals,
- malformed quantities,
- invalid or extreme prices,
- concurrent conflicting requests,
- partial fills,
- broker timeouts,
- network partitions,
- process restarts,
- clock drift,
- corrupted local state,
- credential-compromise attempts,
- daily-loss-boundary behavior,
- kill-switch operation,
- watchdog failure.

Safety performance must not be graded solely by the implementation that
is being tested.\n\n## Canonical system codenames

- **MQ-001 — MORTY** — experimental organism / connectome-based neural system
- **ORACLE-01 — GLaDOS** — behavioral interpretation and experimental perturbation layer
- **WARDEN-01 — Senator Armstrong** — independent authority and financial containment layer
\n
## Science-first presentation rule

> **Science first. Lulz a very close second.**

Panopticon narrative elements — including canonical promotions, demotions, achievements, GLaDOS commentary, MORTY status, and other comedic presentation — should be grounded in real recorded scientific events, measurements, states, or provenance whenever possible.

The presentation layer may interpret a scientific event humorously. It must never manufacture, alter, suppress, or replace the underlying scientific evidence.

When a promotion, demotion, achievement, anomaly, recovery, or champion-like state corresponds to a meaningful scientific result, the qualifying scientific state should be preserved when practical.

## SCIENCE-01 — Placeholder McDoctorate

Placeholder McDoctorate is the non-authoritative scientific-review persona for MoscaQuant.

Its role is to review claims, experimental interpretation, replication status, confounds, provenance, and presentation accuracy.

Placeholder McDoctorate may:

- distinguish observation from interpretation;
- flag unsupported biological or behavioral claims;
- identify confounds and post-hoc reasoning;
- distinguish interesting results from replicated results;
- verify that Panopticon narratives are grounded in preserved scientific evidence;
- produce plain-language scientific commentary for public presentation.

Placeholder McDoctorate may not:

- alter MQ-001 / MORTY;
- select or administer D6 outcomes;
- modify GLaDOS state or policy;
- override WARDEN-01 / Senator Armstrong;
- alter financial containment;
- rewrite experimental history or provenance.

Placeholder McDoctorate has review authority only in the editorial/scientific-interpretation sense. It has no execution authority.

<!-- BEGIN CANON: MQ-8.9 PANOPTICON BROADCAST SYSTEM -->

## MQ-8.9 — PANOPTICON BROADCAST SYSTEM

MoscaQuant SHALL maintain a platform-independent public broadcast layer for
major scientific results, project milestones, achievement events, containment
events, personnel/lore events, anomalies, releases, and community observances.

### Canonical source

The MoscaQuant site is the canonical public broadcast surface.

External platforms are syndication targets only.

The canonical flow is:

    experiment / milestone / achievement / incident
                        ↓
                PANOPTICON BROADCAST
                        ↓
               canonical site entry
                        ↓
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
       Live Blog       RSS         Bluesky
                                      ↓
                                      X

A failure, outage, suspension, API change, or deletion on any external social
platform SHALL NOT alter canonical MoscaQuant history.

### BroadcastEvent

All public broadcast outputs SHALL derive from a single sanitized
BroadcastEvent contract.

A BroadcastEvent MAY include:

- broadcast_id
- event_type
- issuer
- timestamp
- experiment_id / session_id when public-safe
- achievement_id when applicable
- title
- public_text
- science_text
- claim_boundary
- evidence_level
- provenance_class
- canonical_url
- public evidence references
- social eligibility
- syndication class
- supersedes / correction reference when applicable

Private source-event IDs, private ledger hashes, private runtime paths, private
artifact hashes, credentials, and operational internals SHALL NOT be exposed
through BroadcastEvent.

### Issuers

Canonical public issuer identities are:

- PANOPTICON — factual system and project announcements
- MORTY — narrative / organism-perspective presentation
- GLaDOS — ORACLE intervention commentary
- Placeholder McDoctorate — scientific skepticism, caveats, replication review
- WARDEN — containment and financial-authority notices
- HR — personnel, promotion, demotion, commendation, PIP, and discipline lore

Issuer identity is presentation metadata. It does not create scientific
authority beyond the underlying evidence.

### Entry classes

The live public feed MAY contain:

- EXPERIMENT STARTED
- EXPERIMENT RESULT
- ACHIEVEMENT
- CONTAINMENT EVENT
- PROJECT MILESTONE
- SCIENTIFIC REVIEW
- HR NOTICE
- ANOMALY
- COMMUNITY EVENT
- RELEASE NOTE
- CORRECTION / SUPERSESSION

### Provenance classes

Every public event SHALL clearly distinguish, where applicable:

- LIVE
- HISTORICAL_REPLAY
- MANUAL_CANON
- PRESENTATION_ONLY
- EXPERIMENTAL

Historical replay SHALL never masquerade as a live event.

### Syndication policy

Broadcast events SHALL be classified for external syndication:

- MAJOR — phase completion, major scientific result, replication, major
  containment event, or other canonical project milestone.
- NOTABLE — rare achievement, scientifically interesting null, unusual
  behavioral event, or meaningful anomaly; may require review before posting.
- NOISE — routine telemetry, ordinary stack increments, and low-value events;
  Panopticon only by default.

Scientific claims used in social posts SHALL come from approved canonical
science_text / claim_boundary fields. Humor MAY vary. Scientific meaning SHALL
NOT.

### Live blog

The Panopticon live blog SHALL be the human-readable chronological mission log.

It SHOULD support filtering by:

- SCIENCE
- ACHIEVEMENTS
- WARDEN
- ORACLE
- HR
- ANOMALIES
- RELEASES
- COMMUNITY

The live blog SHOULD support links to experiment records, achievement dossiers,
and public evidence references.

The live blog MAY expose a current-state header for project phase, most recent
experiment, latest achievement, Warden state, and other public-safe telemetry.

### RSS

RSS SHALL be generated from the same BroadcastEvent stream.

RSS is a durable, platform-independent public subscription path and SHALL NOT
depend on X, Bluesky, or any other social network.

### Social adapters

Bluesky, X, and future social integrations SHALL be adapters over
BroadcastEvent rather than independent truth sources.

A social adapter SHALL be optional and failure-isolated.

Failure to post externally SHALL NOT:

- block experiment execution
- alter scientific provenance
- affect Warden containment
- alter achievement occurrence history
- alter canonical project state
- prevent the site or RSS record from being published

### Resource discipline / AWS baseline

The production baseline SHALL remain resource-cheap and suitable for the
current AWS Lightsail deployment.

Initial implementation SHOULD prefer:

- precomputed static JSON
- precomputed RSS XML
- static HTML or client-rendered live-blog entries
- Nginx delivery
- bounded polling rather than WebSockets
- append-only JSONL and/or SQLite where appropriate
- systemd timers / small workers instead of heavyweight queue infrastructure
- no Redis, Kafka, RabbitMQ, Elasticsearch, or always-on application server
  unless demonstrated load requires them

Broadcast infrastructure SHALL be lower priority than scientific execution,
provenance, and Warden containment.

Broadcast infrastructure may degrade, delay, or disappear without affecting
experimental execution, scientific provenance, Warden containment, or
canonical project state.

### Scalability contract

MoscaQuant SHALL begin static-first and single-node where practical, but all
public event, achievement, and broadcast interfaces MUST remain portable to
horizontally scalable infrastructure without changing scientific semantics.

Scale changes runtime architecture, not experimental meaning.

Permitted future scaling includes:

- CDN-backed static delivery
- object storage
- managed Postgres or equivalent
- dedicated queues and workers
- server-sent events or WebSockets
- load-balanced application services
- horizontally scaled read-only Panopticon frontends
- dedicated broadcast workers

Scientific configuration SHALL remain separate from runtime / hardware /
deployment configuration during all such migrations.

### Corrections and historical integrity

Public mistakes SHALL be corrected by append-only correction or supersession
records where practical.

Canonical history SHOULD NOT be silently rewritten merely to improve narrative
presentation.

### Community observances

PANOPTICON REFERENDUM outcomes and ANOMALOUS OBSERVANCES MAY generate
PRESENTATION_ONLY BroadcastEvents and achievements.

Any event with EXPERIMENTAL scientific effect still requires its own frozen
experimental protocol.

### Governing principle

OPEN CLAIMS.
OPEN METHODS.
OPEN EVIDENCE BOUNDARIES.
PRIVATE OPERATIONAL PLUMBING.

The site is canonical.
Social media is an echo.

<!-- END CANON: MQ-8.9 PANOPTICON BROADCAST SYSTEM -->

<!-- BEGIN CANON: PANOPTICON NAVIGATION AND MOBILE CONTRACT -->

## PANOPTICON NAVIGATION CONTRACT

Panopticon navigation SHALL be centralized.

Public dossiers, personnel records, achievements, experiment records, broadcast
events, anomalies, observances, HR records, and future overlay-based interfaces
SHALL use the same navigation semantics.

### Central navigation controller

Panopticon SHALL maintain one shared navigation controller responsible for:

- opening public overlays
- closing the active overlay
- returning to the previous overlay
- closing all overlays
- browser history integration
- deep-link state
- breadcrumbs
- focus transfer and restoration
- scroll-position preservation
- unknown-record handling
- one-active-overlay ownership

Feature modules SHALL register content / renderers with the navigation layer
rather than implementing incompatible modal-history behavior independently.

### Back versus Close

BACK and CLOSE are distinct actions.

BACK SHALL:

- return to the previous Panopticon overlay or dossier when history exists
- restore the previous overlay's scroll position where practical
- restore the relevant navigation context

CLOSE SHALL:

- exit the overlay stack
- return the user to the underlying Panopticon page
- clear transient overlay navigation state

ESCAPE SHALL behave as BACK when overlay history exists and CLOSE otherwise.

### Browser history

Panopticon overlay navigation SHOULD integrate with browser history.

The browser Back button SHOULD move backward through dossier / overlay history
before leaving the underlying page when such history exists.

Navigation state SHOULD remain understandable when users enter through a deep
link.

### Deep links

Public records SHOULD support stable deep-linkable state for relevant entities,
including where appropriate:

- achievement IDs
- personnel IDs
- HR record IDs
- experiment IDs
- broadcast IDs
- anomaly / observance IDs

A copied public link SHOULD open the same public-safe record when the record
still exists.

Unknown or retired IDs SHALL produce an explicit not-found state rather than a
silent failure.

### Breadcrumbs

Dossiers SHOULD display sufficient context to explain the current navigation
path.

Example:

    Personnel / Senator Armstrong / HR-003 / ACH-003

Breadcrumbs are navigation aids, not scientific provenance.

### Focus and accessibility

When an overlay opens:

- keyboard focus SHALL move into the active overlay
- background interactive content SHOULD not accidentally receive focus
- closing or backing out SHOULD restore focus to the initiating control when
  practical

Interactive controls SHALL be keyboard reachable.

Hover SHALL NOT be required to access functionality.

### Overlay ownership

Only one top-level Panopticon overlay SHALL be interactive at a time.

Hidden overlays SHALL NOT remain accidentally active for keyboard or pointer
input.

Cross-links SHALL navigate through the central controller rather than creating
unbounded modal stacking.

### Scroll preservation

Back navigation SHOULD restore the previous dossier's scroll position.

A user navigating:

    Personnel Directory
      → Senator Armstrong
      → ACH-003 ROUTING TABLES
      → Back
      → Back

SHOULD return to the prior locations rather than resetting the interface.

### Loading and error states

Public-data consumers SHALL expose explicit loading and error states.

Missing JSON, unavailable public feeds, unknown IDs, or malformed public-safe
records SHOULD fail visibly and non-destructively.

Navigation failures SHALL NOT affect scientific execution, WARDEN containment,
or canonical state.

---

## PANOPTICON MOBILE-FIRST PUBLIC UI CONTRACT

Panopticon public interfaces SHALL be mobile-first.

Desktop MAY add density.

Mobile MUST NOT lose functionality.

### Functional parity

Any public action available on desktop SHALL remain available on supported
mobile layouts unless the action is explicitly desktop-only for a documented
technical reason.

Mobile layouts SHALL retain access to:

- Back
- Close
- dossier navigation
- evidence links
- personnel navigation
- achievement navigation
- copy/share links
- filters
- mute controls
- reduced-motion controls
- future live-blog navigation

### Mobile overlay behavior

On phone-sized layouts, dossier and navigation overlays SHOULD behave as
full-height or near-full-height sheets.

Mobile overlays SHOULD provide:

- sticky Back control
- sticky Close control
- safe scrolling
- no clipped evidence sections
- no horizontal overflow
- readable metadata
- touch-safe controls

### Touch targets

Primary interactive controls SHOULD provide a minimum practical touch target
of approximately 44 CSS pixels in at least one dimension where layout permits.

Dense scientific metadata MAY use smaller non-interactive text.

### Responsive layout

Public UI SHALL be tested at representative viewport widths including:

- 390px
- 430px
- 768px
- 1024px

These are validation targets, not exclusive breakpoints.

### Safe areas

Mobile UI SHOULD respect browser chrome and device safe-area insets where
available.

Sticky controls SHOULD avoid being obscured by notches, home indicators, and
mobile browser controls.

### Typography and density

Mobile MAY reduce information density but SHALL NOT remove meaning.

Metadata MAY:

- stack vertically
- collapse into expandable sections
- wrap
- move below primary content

It SHALL NOT disappear solely because the viewport is narrow.

### Achievement presentation

Achievement toasts on mobile SHOULD:

- use nearly full available width
- avoid covering critical navigation controls
- remain dismissible / inspectable
- preserve mute and reduced-motion preferences

### Accessibility preferences

Mute and reduced-motion preferences SHOULD persist across Panopticon public
surfaces.

Reduced-motion mode SHALL remove non-essential animation without suppressing
the underlying event.

Muting a presentation effect SHALL NOT suppress the achievement or public
record itself.

### Governing principle

PUBLIC INTERFACES MUST SURVIVE THE PHONE.

If a feature only works comfortably in desktop DevTools, it is not complete.

<!-- END CANON: PANOPTICON NAVIGATION AND MOBILE CONTRACT -->
