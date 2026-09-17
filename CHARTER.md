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

WARDEN-01 is the independent risk and execution authority.

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

MQ-5 — DEPLOY THE WARDEN

Deploy independent risk gateway and conduct adversarial testing.

MQ-6 — AWAKEN THE ORACLE

Implement and validate the complete D6 protocol.

MQ-7 — CORPORATE CULTURE

Implement achievements, personnel records, reviews and related systems.

MQ-8 — OPEN THE PANOPTICON

Deploy the public spectator environment and Containment Chamber.

MQ-9 — INTRODUCE THE MONEY

Connect supported broker infrastructure in read-only mode.

MQ-10 — THE CASINO OPENS

Permit tiny controlled real-money transactions through WARDEN-01.

MQ-11 — CONSEQUENCES

Enable experimental plasticity and persistent aversive learning.

MQ-12 — MOSCA VS THE WORLD

Conduct comparative experiments against controls and benchmarks.

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

Git history is the authoritative project record.

29. Current Directive
YOLO & HODL LLC
MOSCAQUANT

SUBJECT ................. MQ-001
CURRENT PHASE ........... MQ-4
MISSION ................. NEUROSCOPE

BROKER .................. NONE
TRADING AUTHORITY ....... NONE
ORACLE .................. DORMANT
WARDEN-01 ............... NOT DEPLOYED
PANOPTICON .............. NOT DEPLOYED

CONTAINMENT ............. ACTIVE

FINANCIAL SEMANTICS ..... NOT ASSIGNED

NEXT OBJECTIVE:

BUILD NEUROSCOPE FROM FROZEN MQ-1 THROUGH MQ-3 TELEMETRY WITHOUT ALTERING THE EXPERIMENTAL MODEL.

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
is being tested.
